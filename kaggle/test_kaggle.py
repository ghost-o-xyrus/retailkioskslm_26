"""Tests for the Kaggle runner (no Kaggle account or network needed)."""

import json
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import push_job as P  # noqa: E402
import pull_job as Q  # noqa: E402


class KaggleRunnerTests(unittest.TestCase):
    def test_bundle_contents(self):
        names = {a for _, a in P.bundle_files(["eval/rag_cases.jsonl"])}
        self.assertIn("harness/run_eval.py", names)
        self.assertIn("knowledge/corpus.jsonl", names)
        self.assertIn("kaggle/kernel_main.py", names)
        self.assertFalse(any(n.startswith(("results", "models/", "kaggle/_staging", "kaggle/_pulled")) for n in names))
        self.assertFalse(any(n.endswith((".gguf", ".pyc")) or "__pycache__" in n for n in names))

    def test_plan_job_runs_cpu_runs_only(self):
        name, job = P.plan_job(os.path.join(ROOT, "harness", "plans", "obj3_step6_speed.json"))
        self.assertEqual(name, "plan_obj3_step6_speed")
        self.assertIn("--only-backend cpu", job["commands"][0])
        self.assertTrue(job["needs_llama"] and job["needs_models"])
        self.assertTrue(all(o.startswith("results_obj3/") for o in job["outputs"]))
        with self.assertRaises(SystemExit):           # a Vulkan-only plan has nothing to send
            P.plan_job(os.path.join(ROOT, "harness", "plans", "obj3_step8.json"))

    def test_kernel_runs_job_and_packs_changed_outputs(self):
        job = {"description": "t", "pip": [], "inputs": [], "outputs": ["results_obj3/_kaggle_test"],
               "commands": ["python -c \"import os; os.makedirs('results_obj3/_kaggle_test', exist_ok=True); "
                            "open('results_obj3/_kaggle_test/machine.txt', 'w').write(os.environ['SLM_MACHINE'])\""]}
        code, kern, kid = P.build("unit_test", job, "someone")
        with open(os.path.join(kern, "kernel-metadata.json"), encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(kid, "someone/slm-kiosk-unit-test")
        self.assertTrue(meta["is_private"] and meta["enable_internet"] and not meta["enable_gpu"])
        self.assertEqual(meta["dataset_sources"], ["someone/slm-kiosk-code"])
        with tempfile.TemporaryDirectory() as t:
            inp, work = os.path.join(t, "input", "slm-kiosk-code"), os.path.join(t, "working")
            os.makedirs(inp)
            os.replace(os.path.join(code, "project.zip"), os.path.join(inp, "project.zip"))
            env = dict(os.environ, KAGGLE_INPUT_DIR=os.path.join(t, "input"), KAGGLE_WORKING_DIR=work,
                       SLM_PROJ_DIR=os.path.join(t, "proj"), SLM_SKIP_PIP="1")
            r = subprocess.run([sys.executable, os.path.join(kern, "run_job.py")], env=env, capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            with open(os.path.join(work, "status.json"), encoding="utf-8") as f:
                st = json.load(f)
            self.assertTrue(st["ok"], st)
            self.assertEqual(st["files"], ["results_obj3/_kaggle_test/machine.txt"])
            dest = os.path.join(t, "laptop")
            os.makedirs(dest)
            self.assertEqual(Q.unpack(os.path.join(work, "job_output.zip"), dest), ["results_obj3/_kaggle_test/machine.txt"])
            with open(os.path.join(dest, "results_obj3", "_kaggle_test", "machine.txt")) as f:
                self.assertEqual(f.read(), "kaggle-cpu")

    def test_unpack_refuses_paths_outside(self):
        with tempfile.TemporaryDirectory() as t:
            z = os.path.join(t, "bad.zip")
            with zipfile.ZipFile(z, "w") as zz:
                zz.writestr("../escape.txt", "x")
            os.makedirs(os.path.join(t, "root"))
            with self.assertRaises(SystemExit):
                Q.unpack(z, os.path.join(t, "root"))


class LlamaFetchTests(unittest.TestCase):
    """The Step 5 smoke failure: the laptop's version line read as 'b0', and the release had no asset of the
    old name. Version parsing, asset choice, unpacking and pip pinning, without the network."""

    def test_version_lines(self):
        from kaggle import push_job as P
        self.assertEqual(P.parse_llama_version("version: 6123 (abc1234)\nbuilt with MSVC"), "b6123")
        self.assertEqual(P.parse_llama_version("version: 12109 (abc1234)"), "b12109")
        self.assertEqual(P.parse_llama_version("version: 0.9.0 (abc1234)"), "v0.9.0")
        self.assertEqual(P.parse_llama_version("version: v0.9.0 (abc1234)"), "v0.9.0")
        self.assertIsNone(P.parse_llama_version("version: 0 (unknown)"))
        self.assertIsNone(P.parse_llama_version("nothing here"))

    def test_asset_choice(self):
        from kaggle import kernel_main as K
        names = ["llama-v0.9.0-bin-macos-arm64.tar.gz", "llama-v0.9.0-bin-ubuntu-vulkan-x64.tar.gz",
                 "llama-v0.9.0-bin-ubuntu-x64.tar.gz", "llama-v0.9.0-bin-win-cpu-x64.zip",
                 "llama-v0.9.0-bin-ubuntu-arm64.tar.gz", "llama-v0.9.0-bin-ubuntu-cuda-12.4-x64.tar.gz"]
        pick = K._pick_linux_cpu([(n, "u/" + n) for n in names])
        self.assertEqual([n for n, _ in pick], ["llama-v0.9.0-bin-ubuntu-x64.tar.gz"])
        self.assertEqual([n for n, _ in K._pick_linux_cpu([("llama-b6123-bin-ubuntu-x64.zip", "u")])],
                         ["llama-b6123-bin-ubuntu-x64.zip"])
        self.assertEqual(K._pick_linux_cpu([("llama-b1-bin-win-cpu-x64.zip", "u")]), [])
        real = ["llama-b10566-bin-ubuntu-x64.tar.gz", "llama-b10566-bin-ubuntu-arm64.tar.gz",       # a real release
                "llama-b10566-bin-ubuntu-s390x.tar.gz", "llama-b10566-bin-ubuntu-vulkan-x64.tar.gz",
                "llama-b10566-bin-ubuntu-openvino-2026.3-x64.tar.gz", "llama-b10566-bin-ubuntu-sycl-fp32-x64.tar.gz",
                "llama-b10566-bin-macos-x64.tar.gz", "llama-b10566-bin-android-arm64.tar.gz",
                "llama-b10566-bin-win-cpu-x64.zip", "llama-b10566-ui.tar.gz", "llama-b10566-xcframework.zip"]
        self.assertEqual([n for n, _ in K._pick_linux_cpu([(n, "u") for n in real])],
                         ["llama-b10566-bin-ubuntu-x64.tar.gz"])

    def test_unpack_tar_and_zip(self):
        import tarfile
        from kaggle import kernel_main as K
        for kind in ("tar.gz", "zip"):
            with tempfile.TemporaryDirectory() as t:
                src = os.path.join(t, "src", "build", "bin")
                os.makedirs(src)
                with open(os.path.join(src, "llama-server"), "w") as f:
                    f.write("#!/bin/sh\n")
                arc = os.path.join(t, "a." + kind)
                if kind == "zip":
                    with zipfile.ZipFile(arc, "w") as z:
                        z.write(os.path.join(src, "llama-server"), "build/bin/llama-server")
                else:
                    with tarfile.open(arc, "w:gz") as z:
                        z.add(os.path.join(t, "src", "build"), "build")
                dest = os.path.join(t, "dest")
                os.makedirs(dest)
                K._unpack(arc, dest)
                exe = K._found_server(dest)
                self.assertTrue(exe and exe.endswith("build/bin/llama-server"), exe)
                self.assertTrue(os.access(exe, os.X_OK))

    def test_install_pins_plain_names_only_and_installs_the_rest(self):
        from kaggle import kernel_main as K
        cmds = []
        old_run, old_skip = K.run, os.environ.pop("SLM_SKIP_PIP", None)
        K.run = lambda c, **kw: cmds.append(c) or 0
        try:
            K.install({"pip": ["huggingface_hub", "transformers>=5"],
                       "requirements": ["transformers==4.57.6", "huggingface_hub==0.36.2"]})
            self.assertEqual(len(cmds), 2, cmds)
            self.assertIn('"huggingface_hub==0.36.2"', cmds[0])
            self.assertNotIn("4.57.6", " ".join(cmds))
            self.assertIn('"transformers>=5"', cmds[1])
            cmds.clear()
            K.install({"pip": ["psutil", "numpy"], "requirements": ["psutil==5.9.0"]})
            self.assertIn('"psutil==5.9.0"', cmds[0])
            self.assertIn('"numpy"', cmds[1])
        finally:
            K.run = old_run
            if old_skip is not None:
                os.environ["SLM_SKIP_PIP"] = old_skip

    def test_step5_jobs_need_transformers_5(self):
        with open(os.path.join(ROOT, "kaggle", "jobs.json"), encoding="utf-8") as f:
            jobs = json.load(f)
        for k in ("o4_step5_smoke", "o4_step5"):
            self.assertIn("transformers>=5", jobs[k]["pip"])
            self.assertTrue(jobs[k]["needs_llama"])


if __name__ == "__main__":
    unittest.main()

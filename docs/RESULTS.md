# Results, logs and job data: where everything is

Written by `publish/prepare_repo.py`. Folder names are the ones the code writes to, so every script and plan in the repository still finds its inputs. A folder's own `report.md`, where there is one, is the place to start; the reports in `writeups/` cite these folders.

"On Drive" counts files that were too large for GitHub: see [LARGE_FILES.md](LARGE_FILES.md).

## `results/`

Objective 1: choosing the model (screening, number format, head-to-head, speed).

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `_scores/` | 58 | 2.4 MB |  | Scores (test split) |
| `gemma4-e2b_q4_k_m_vulkan/` | 5 | 0.5 MB |  |  |
| `gemma4-e2b_q8_0_cpu_speed/` | 5 | 0.1 MB |  |  |
| `gemma4-e2b_q8_0_vulkan/` | 4 | 0.5 MB |  |  |
| `gemma4-e2b_q8_0_vulkan_speed/` | 5 | 0.1 MB |  |  |
| `gemma4-e2b_q8_0_vulkan_v11_greedy/` | 5 | 1.1 MB |  |  |
| `llama32-3b_q4_k_m_vulkan/` | 5 | 1.0 MB |  |  |
| `o3s13a2_4b_rag/` | 4 | 0.7 MB |  |  |
| `phi4-mini_q4_k_m_vulkan/` | 4 | 0.3 MB |  |  |
| `pilot_qwen35-4b/` | 4 | 68.7 KB |  |  |
| `qwen35-0.8b_q4_k_m_vulkan/` | 5 | 0.4 MB |  |  |
| `qwen35-2b_bf16_vulkan_speed/` | 5 | 0.1 MB |  |  |
| `qwen35-2b_bf16_vulkan_v11_greedy/` | 4 | 1.3 MB |  |  |
| `qwen35-2b_q4_k_m_vulkan/` | 4 | 0.6 MB |  |  |
| `qwen35-2b_q4_k_m_vulkan_v11_greedy/` | 5 | 1.2 MB |  |  |
| `qwen35-2b_q4_k_m_vulkan_v11_t03/` | 5 | 3.4 MB |  |  |
| `qwen35-2b_q8_0_cpu_speed/` | 5 | 0.1 MB |  |  |
| `qwen35-2b_q8_0_vulkan/` | 5 | 0.7 MB |  |  |
| `qwen35-2b_q8_0_vulkan_speed/` | 4 | 0.1 MB |  |  |
| `qwen35-2b_q8_0_vulkan_v11_greedy/` | 5 | 1.3 MB |  |  |
| `qwen35-4b_q4_k_m_cpu_speed/` | 5 | 0.1 MB |  |  |
| `qwen35-4b_q4_k_m_vulkan/` | 5 | 0.6 MB |  |  |
| `qwen35-4b_q4_k_m_vulkan_speed/` | 5 | 0.1 MB |  |  |
| `qwen35-4b_q4_k_m_vulkan_v11_greedy/` | 5 | 1.2 MB |  |  |
| `qwen35-4b_q4_k_m_vulkan_v11_t03/` | 5 | 3.7 MB |  |  |
| `qwen35-4b_q8_0_vulkan/` | 5 | 0.6 MB |  |  |
| (files directly in `results/`) | 1 | 92.9 KB | | |

## `results_obj2/`

Objective 2: the model with retrieval (pilots and the confirming run).

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `_compare/` | 2 | 6.9 KB |  |  |
| `_pilot/` | 1 | 2.0 KB |  | Step 7 pilot (dev cases only; rough checks, not the Step 8 score) |
| `_scores_p7d/` | 12 | 74.4 KB |  | Scores (dev split) |
| `_scores_step8/` | 16 | 0.6 MB |  | Step 8: end-to-end results on the test retrieval questions |
| `_scores_step8_speed/` | 5 | 15.8 KB |  | Step 8: end-to-end results on the test retrieval questions |
| `_scores_step8_v11/` | 16 | 0.8 MB |  | Scores (test split, tools cases) |
| `_time_split_s8/` | 3 | 0.2 MB |  | Where the time goes (Objective 3, Step 1) |
| `_time_split_s8sp/` | 3 | 39.9 KB |  | Where the time goes (Objective 3, Step 1) |
| `p7_2b_cpu_rag_always/` | 4 | 0.2 MB |  |  |
| `p7_2b_cpu_rag_none/` | 3 | 0.1 MB |  |  |
| `p7_4b_rag_always/` | 4 | 99.0 KB |  |  |
| `p7_4b_rag_gate/` | 4 | 0.1 MB |  |  |
| `p7_4b_rag_none/` | 4 | 0.1 MB |  |  |
| `p7_4b_rag_oracle/` | 4 | 86.4 KB |  |  |
| `p7_4b_rag_tool/` | 4 | 0.2 MB |  |  |
| `p7_4b_v11_always/` | 4 | 0.1 MB |  |  |
| `p7_4b_v11_none/` | 4 | 94.7 KB |  |  |
| `p7d_2b_cpu_rag_compact_chunkgate/` | 4 | 0.2 MB |  |  |
| `p7d_2b_cpu_rag_compact_gate/` | 4 | 0.2 MB |  |  |
| `p7d_2b_cpu_rag_full_gate/` | 4 | 0.2 MB |  |  |
| `p7d_2b_cpu_v11_compact_chunkgate/` | 4 | 0.2 MB |  |  |
| `p7d_2b_cpu_v11_compact_gate/` | 4 | 0.2 MB |  |  |
| `p7d_2b_cpu_v11_full_gate/` | 4 | 0.2 MB |  |  |
| `p7d_2b_cpu_v11_none/` | 4 | 0.1 MB |  |  |
| `p7e_2b_cpu_rag_omit/` | 4 | 0.2 MB |  |  |
| `p7e_2b_cpu_rag_rulec/` | 4 | 0.2 MB |  |  |
| `p7e_2b_cpu_v11_omit/` | 4 | 0.2 MB |  |  |
| `p7e_2b_cpu_v11_rulec/` | 4 | 0.2 MB |  |  |
| `p7f_2b_cpu_rag_dedupe/` | 4 | 0.2 MB |  |  |
| `p7f_2b_cpu_v11_dedupe/` | 4 | 0.2 MB |  |  |
| `s8_2b_rag_deployed/` | 4 | 2.5 MB |  |  |
| `s8_2b_rag_nofallback/` | 4 | 2.6 MB |  |  |
| `s8_2b_rag_none/` | 4 | 1.9 MB |  |  |
| `s8_2b_rag_oracle/` | 4 | 1.8 MB |  |  |
| `s8_2b_rag_tool/` | 4 | 2.0 MB |  |  |
| `s8_2b_v11_deployed/` | 4 | 2.0 MB |  |  |
| `s8_2b_v11_none/` | 4 | 1.4 MB |  |  |
| `s8_4b_rag_deployed/` | 4 | 1.6 MB |  |  |
| `s8_4b_rag_nofallback/` | 4 | 1.5 MB |  |  |
| `s8_4b_rag_none/` | 4 | 2.0 MB |  |  |
| `s8_4b_rag_oracle/` | 4 | 1.2 MB |  |  |
| `s8_4b_rag_tool/` | 4 | 2.4 MB |  |  |
| `s8_4b_v11_deployed/` | 4 | 1.5 MB |  |  |
| `s8_4b_v11_none/` | 4 | 1.3 MB |  |  |
| `s8sp_2b_cpu_rag_deployed/` | 4 | 0.2 MB |  |  |
| `s8sp_2b_cpu_rag_none/` | 3 | 0.2 MB |  |  |
| `s8sp_2b_cpu_v11_deployed/` | 4 | 0.2 MB |  |  |
| `s8sp_2b_cpu_v11_none/` | 3 | 0.1 MB |  |  |

## `results_retrieval/`

Objective 2: retrieval benchmarks, fallback calibration, integration settings.

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `fallback/` | 4 | 51.4 KB |  | Step 6: refusal fallback calibration |
| `fallback_bypass/` | 4 | 50.9 KB |  | Step 6: refusal fallback calibration (with Hinglish bypass) |
| `integration/` | 4 | 4.6 KB |  | Step 7a: knowledge base check |
| `latency/` | 30 | 4.7 MB | 2 | Step 5b: retriever latency variants |
| `ranks/` | 21 | 5.2 MB |  |  |
| (files directly in `results_retrieval/`) | 3 | 15.5 KB | | |

## `results_obj3/`

Objective 3: the harness (thirteen changes on development data, the test-set run, the ladder).

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `_compare_step10/` | 3 | 0.1 MB |  | Paired dev comparison (Objective 3) |
| `_compare_step11/` | 3 | 71.1 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step11b/` | 3 | 33.0 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step12/` | 3 | 35.8 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step13/` | 3 | 80.9 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step13a2/` | 3 | 0.1 MB |  | Paired dev comparison (Objective 3) |
| `_compare_step14/` | 3 | 0.3 MB |  | Paired dev comparison (Objective 3) |
| `_compare_step14_speed/` | 3 | 40.2 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step2/` | 2 | 13.1 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step3/` | 2 | 14.2 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step3_guard/` | 2 | 14.1 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step3_vs_b0/` | 2 | 9.8 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step4/` | 2 | 20.6 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step4_vs_noretrieval/` | 2 | 9.5 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step5/` | 2 | 21.5 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step5_harness_only/` | 2 | 14.4 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step6/` | 3 | 22.5 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step6c/` | 3 | 23.6 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step7/` | 3 | 41.5 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step7a/` | 3 | 39.8 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step8/` | 3 | 24.7 KB |  | Paired dev comparison (Objective 3) |
| `_compare_step8a/` | 3 | 13.1 KB |  | Paired dev comparison (Objective 3) |
| `_dialogues_step13/` | 3 | 40.6 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_dialogues_step14/` | 3 | 57.4 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_dialogues_step6/` | 2 | 6.0 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_dialogues_step6b/` | 3 | 45.2 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_dialogues_step6c/` | 3 | 45.5 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_dialogues_step7/` | 3 | 41.0 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_noise_floor/` | 2 | 3.0 KB |  | Noise floor: identical greedy repeats (Objective 3, Step 2) |
| `_old_step13b/` | 70 | 2.8 MB |  |  |
| `_rerank_step9/` | 10 | 0.3 MB |  | Step 9: re-ranker trial (dev retrieval questions) |
| `_router_dev/` | 3 | 53.3 KB |  | Router check (dev split, rules + bge-small prototypes) |
| `_rubric_step6/` | 2 | 22.9 KB |  |  |
| `_rubric_step6_2b/` | 4 | 13.7 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_rubric_step6_4b/` | 4 | 17.7 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_scores_step1_rag/` | 8 | 0.1 MB |  | Step 8: end-to-end results on the test retrieval questions |
| `_scores_step1_v11/` | 12 | 0.2 MB |  | Scores (dev split, tools cases) |
| `_scores_step1_v11_credit/` | 12 | 0.2 MB |  | Scores (dev split, tools cases) |
| `_smoke15/` | 36 | 0.3 MB |  |  |
| `_smoke15g/` | 12 | 0.1 MB |  |  |
| `_spec_step13b/` | 2 | 17.2 KB |  | Step 13b: speculative decoding (dev speed subset, greedy) |
| `_speed_step12/` | 16 | 0.6 MB |  | Step 12: retrieval speed and RAM (dev) |
| `_step14/` | 2 | 9.0 KB |  |  |
| `_step15/` | 7 | 0.8 MB |  |  |
| `_step15_gpu/` | 5 | 2.0 MB |  |  |
| `_tau_step8/` | 2 | 1.5 KB |  | Step 8: hard-fallback threshold on dev store questions |
| `_time_split_quality/` | 3 | 0.2 MB |  | Where the time goes (Objective 3, Step 1) |
| `_time_split_speed/` | 3 | 85.5 KB |  | Where the time goes (Objective 3, Step 1) |
| `_time_split_step2/` | 3 | 88.4 KB |  | Where the time goes (Objective 3, Step 1) |
| `_time_split_step3/` | 3 | 0.2 MB |  | Where the time goes (Objective 3, Step 1) |
| `_time_split_step3_pilot/` | 3 | 14.0 KB |  | Where the time goes (Objective 3, Step 1) |
| `_time_split_step4/` | 3 | 0.1 MB |  | Where the time goes (Objective 3, Step 1) |
| `_time_split_step5/` | 3 | 0.2 MB |  | Where the time goes (Objective 3, Step 1) |
| `o3g_b0_2b_dlg/` | 4 | 0.8 MB |  |  |
| `o3g_b0_2b_fup/` | 4 | 0.4 MB |  |  |
| `o3g_b0_2b_rag/` | 4 | 3.4 MB |  |  |
| `o3g_b0_2b_v12/` | 4 | 1.7 MB |  |  |
| `o3g_b0_4b_dlg/` | 3 | 0.7 MB |  |  |
| `o3g_b0_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3g_b0_4b_rag/` | 4 | 2.1 MB |  |  |
| `o3g_b0_4b_v12/` | 4 | 1.2 MB |  |  |
| `o3g_nr_2b_dlg/` | 4 | 0.8 MB |  |  |
| `o3g_nr_2b_fup/` | 3 | 0.3 MB |  |  |
| `o3g_nr_2b_rag/` | 4 | 3.0 MB |  |  |
| `o3g_nr_2b_v12/` | 4 | 1.5 MB |  |  |
| `o3g_nr_4b_dlg/` | 3 | 0.7 MB |  |  |
| `o3g_nr_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3g_nr_4b_rag/` | 4 | 2.3 MB |  |  |
| `o3g_nr_4b_v12/` | 4 | 1.3 MB |  |  |
| `o3g_r1_2b_dlg/` | 4 | 0.9 MB |  |  |
| `o3g_r1_2b_fup/` | 4 | 0.3 MB |  |  |
| `o3g_r1_2b_rag/` | 4 | 3.2 MB |  |  |
| `o3g_r1_2b_v12/` | 4 | 1.6 MB |  |  |
| `o3g_r1_4b_dlg/` | 3 | 0.7 MB |  |  |
| `o3g_r1_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3g_r1_4b_rag/` | 4 | 2.1 MB |  |  |
| `o3g_r1_4b_v12/` | 4 | 1.3 MB |  |  |
| `o3g_r2_2b_dlg/` | 3 | 0.7 MB |  |  |
| `o3g_r2_2b_fup/` | 4 | 0.4 MB |  |  |
| `o3g_r2_2b_rag/` | 4 | 3.0 MB |  |  |
| `o3g_r2_2b_v12/` | 4 | 1.2 MB |  |  |
| `o3g_r2_4b_dlg/` | 3 | 0.7 MB |  |  |
| `o3g_r2_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3g_r2_4b_rag/` | 4 | 2.2 MB |  |  |
| `o3g_r2_4b_v12/` | 4 | 1.2 MB |  |  |
| `o3g_r3_2b_dlg/` | 3 | 0.4 MB |  |  |
| `o3g_r3_2b_fup/` | 4 | 0.4 MB |  |  |
| `o3g_r3_2b_rag/` | 4 | 3.0 MB |  |  |
| `o3g_r3_2b_v12/` | 4 | 0.8 MB |  |  |
| `o3g_r3_4b_dlg/` | 3 | 0.4 MB |  |  |
| `o3g_r3_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3g_r3_4b_rag/` | 4 | 2.1 MB |  |  |
| `o3g_r3_4b_v12/` | 4 | 0.8 MB |  |  |
| `o3g_r4_2b_dlg/` | 3 | 0.4 MB |  |  |
| `o3g_r4_2b_fup/` | 4 | 0.4 MB |  |  |
| `o3g_r4_2b_rag/` | 4 | 2.9 MB |  |  |
| `o3g_r4_2b_v12/` | 4 | 0.9 MB |  |  |
| `o3g_r4_4b_dlg/` | 3 | 0.4 MB |  |  |
| `o3g_r4_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3g_r4_4b_rag/` | 4 | 2.0 MB |  |  |
| `o3g_r4_4b_v12/` | 4 | 0.8 MB |  |  |
| `o3g_r5_2b_dlg/` | 3 | 0.4 MB |  |  |
| `o3g_r5_2b_fup/` | 4 | 0.3 MB |  |  |
| `o3g_r5_2b_rag/` | 4 | 3.0 MB |  |  |
| `o3g_r5_2b_v12/` | 4 | 0.9 MB |  |  |
| `o3g_r5_4b_dlg/` | 3 | 0.4 MB |  |  |
| `o3g_r5_4b_fup/` | 3 | 0.2 MB |  |  |
| `o3g_r5_4b_rag/` | 4 | 2.1 MB |  |  |
| `o3g_r5_4b_v12/` | 4 | 0.8 MB |  |  |
| `o3g_r6_2b_dlg/` | 3 | 0.4 MB |  |  |
| `o3g_r6_2b_fup/` | 3 | 0.3 MB |  |  |
| `o3g_r6_2b_rag/` | 4 | 2.7 MB |  |  |
| `o3g_r6_2b_v12/` | 4 | 0.8 MB |  |  |
| `o3g_r6_4b_dlg/` | 3 | 0.4 MB |  |  |
| `o3g_r6_4b_fup/` | 3 | 0.2 MB |  |  |
| `o3g_r6_4b_rag/` | 4 | 2.2 MB |  |  |
| `o3g_r6_4b_v12/` | 4 | 0.8 MB |  |  |
| `o3l_b0_2b_dlg/` | 4 | 0.9 MB |  |  |
| `o3l_b0_2b_fup/` | 4 | 0.4 MB |  |  |
| `o3l_b0_2b_rag/` | 4 | 3.5 MB |  |  |
| `o3l_b0_2b_v12/` | 4 | 1.8 MB |  |  |
| `o3l_b0_4b_dlg/` | 4 | 0.8 MB |  |  |
| `o3l_b0_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3l_b0_4b_rag/` | 4 | 2.2 MB |  |  |
| `o3l_b0_4b_v12/` | 4 | 1.3 MB |  |  |
| `o3l_r5_2b_rag/` | 4 | 3.2 MB |  |  |
| `o3l_r5_4b_rag/` | 4 | 2.2 MB |  |  |
| `o3l_r6_2b_dlg/` | 3 | 0.4 MB |  |  |
| `o3l_r6_2b_fup/` | 3 | 0.3 MB |  |  |
| `o3l_r6_2b_rag/` | 4 | 2.9 MB |  |  |
| `o3l_r6_2b_v12/` | 4 | 0.9 MB |  |  |
| `o3l_r6_4b_dlg/` | 3 | 0.5 MB |  |  |
| `o3l_r6_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3l_r6_4b_rag/` | 4 | 2.2 MB |  |  |
| `o3l_r6_4b_v12/` | 4 | 0.9 MB |  |  |
| `o3l_ref_2b_none/` | 4 | 1.3 MB |  |  |
| `o3l_ref_2b_oracle/` | 4 | 2.7 MB |  |  |
| `o3l_ref_4b_none/` | 4 | 1.1 MB |  |  |
| `o3l_ref_4b_oracle/` | 4 | 1.8 MB |  |  |
| `o3s10_2b_fup/` | 4 | 0.4 MB |  |  |
| `o3s10_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3s10c_2b_rag/` | 4 | 1.0 MB |  |  |
| `o3s10c_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s10c_4b_rag/` | 4 | 0.7 MB |  |  |
| `o3s10c_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s10v_2b_rag/` | 2 | 0.7 MB |  |  |
| `o3s10v_2b_v12/` | 2 | 0.2 MB |  |  |
| `o3s10v_4b_rag/` | 2 | 0.5 MB |  |  |
| `o3s10v_4b_v12/` | 2 | 0.2 MB |  |  |
| `o3s11_2b_fup/` | 4 | 0.3 MB |  |  |
| `o3s11_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s11_4b_fup/` | 4 | 0.2 MB |  |  |
| `o3s11_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s11b_2b_fup/` | 4 | 0.3 MB |  |  |
| `o3s11b_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s11b_4b_fup/` | 3 | 0.2 MB |  |  |
| `o3s11b_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s11q_2b_fup/` | 4 | 0.4 MB |  |  |
| `o3s11q_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s11q_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3s11q_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s12_2b_fup/` | 4 | 0.3 MB |  |  |
| `o3s12_2b_rag/` | 4 | 1.0 MB |  |  |
| `o3s12_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s12_4b_fup/` | 3 | 0.2 MB |  |  |
| `o3s12_4b_rag/` | 4 | 0.6 MB |  |  |
| `o3s12_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s12d_2b/` | 3 | 0.3 MB |  |  |
| `o3s12d_4b/` | 3 | 0.3 MB |  |  |
| `o3s13a2_2b_fup/` | 3 | 0.3 MB |  |  |
| `o3s13a2_2b_rag/` | 4 | 0.9 MB |  |  |
| `o3s13a2_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s13a2_4b_fup/` | 3 | 0.3 MB |  |  |
| `o3s13a2_4b_rag/` | 4 | 0.7 MB |  |  |
| `o3s13a2_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s13a_2b_fup/` | 3 | 0.3 MB |  |  |
| `o3s13a_2b_rag/` | 4 | 0.9 MB |  |  |
| `o3s13a_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s13a_4b_fup/` | 3 | 0.3 MB |  |  |
| `o3s13a_4b_rag/` | 4 | 0.7 MB |  |  |
| `o3s13a_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s13ad_2b/` | 3 | 0.3 MB |  |  |
| `o3s13ad_4b/` | 3 | 0.3 MB |  |  |
| `o3s13b_a_2b_rag_mtp2/` | 4 | 0.3 MB |  |  |
| `o3s13b_a_2b_rag_mtp6/` | 4 | 0.3 MB |  |  |
| `o3s13b_a_2b_rag_mtpfile/` | 4 | 0.3 MB |  |  |
| `o3s13b_a_2b_rag_ngram-mod/` | 4 | 0.3 MB |  |  |
| `o3s13b_a_2b_rag_ngram-simple/` | 4 | 0.3 MB |  |  |
| `o3s13b_a_2b_rag_none/` | 4 | 0.3 MB |  |  |
| `o3s13b_a_2b_rag_none2/` | 4 | 0.3 MB |  |  |
| `o3s13b_a_2b_v12_mtp2/` | 4 | 0.1 MB |  |  |
| `o3s13b_a_2b_v12_mtp6/` | 4 | 0.1 MB |  |  |
| `o3s13b_a_2b_v12_mtpfile/` | 4 | 0.1 MB |  |  |
| `o3s13b_a_2b_v12_ngram-mod/` | 4 | 0.1 MB |  |  |
| `o3s13b_a_2b_v12_ngram-simple/` | 4 | 0.1 MB |  |  |
| `o3s13b_a_2b_v12_none/` | 4 | 0.1 MB |  |  |
| `o3s13b_a_2b_v12_none2/` | 4 | 0.1 MB |  |  |
| `o3s13b_b_4b_rag_draft08/` | 3 | 0.2 MB |  |  |
| `o3s13b_b_4b_rag_mtp2/` | 3 | 0.2 MB |  |  |
| `o3s13b_b_4b_rag_mtp6/` | 3 | 0.2 MB |  |  |
| `o3s13b_b_4b_rag_mtpfile/` | 3 | 0.2 MB |  |  |
| `o3s13b_b_4b_rag_ngram-mod/` | 4 | 0.2 MB |  |  |
| `o3s13b_b_4b_rag_ngram-simple/` | 4 | 0.2 MB |  |  |
| `o3s13b_b_4b_rag_none/` | 4 | 0.2 MB |  |  |
| `o3s13b_b_4b_rag_none2/` | 4 | 0.2 MB |  |  |
| `o3s13b_b_4b_v12_draft08/` | 4 | 0.1 MB |  |  |
| `o3s13b_b_4b_v12_mtp2/` | 4 | 0.1 MB |  |  |
| `o3s13b_b_4b_v12_mtp6/` | 4 | 0.1 MB |  |  |
| `o3s13b_b_4b_v12_mtpfile/` | 4 | 0.1 MB |  |  |
| `o3s13b_b_4b_v12_ngram-mod/` | 4 | 0.1 MB |  |  |
| `o3s13b_b_4b_v12_ngram-simple/` | 4 | 0.1 MB |  |  |
| `o3s13b_b_4b_v12_none/` | 4 | 0.1 MB |  |  |
| `o3s13b_b_4b_v12_none2/` | 4 | 0.1 MB |  |  |
| `o3s13sp2_a_2b_rag_s12/` | 4 | 0.6 MB |  |  |
| `o3s13sp2_a_2b_rag_s13a2/` | 4 | 0.5 MB |  |  |
| `o3s13sp2_a_2b_v12_s12/` | 4 | 0.2 MB |  |  |
| `o3s13sp2_a_2b_v12_s13a2/` | 4 | 0.2 MB |  |  |
| `o3s13sp_a_2b_rag_s12/` | 4 | 0.6 MB |  |  |
| `o3s13sp_a_2b_rag_s13a/` | 4 | 0.5 MB |  |  |
| `o3s13sp_a_2b_v12_s12/` | 4 | 0.2 MB |  |  |
| `o3s13sp_a_2b_v12_s13a/` | 4 | 0.2 MB |  |  |
| `o3s13x_4b_fup_nolen/` | 3 | 0.3 MB |  |  |
| `o3s13x_4b_fup_nopar/` | 3 | 0.3 MB |  |  |
| `o3s13x_4b_rag_nolen/` | 3 | 0.7 MB |  |  |
| `o3s13x_4b_rag_nopar/` | 4 | 0.7 MB |  |  |
| `o3s13x_4b_v12_nolen/` | 4 | 0.3 MB |  |  |
| `o3s13x_4b_v12_nopar/` | 4 | 0.3 MB |  |  |
| `o3s1_2b_rag_b0/` | 4 | 1.0 MB |  |  |
| `o3s1_2b_rag_oracle/` | 4 | 0.8 MB |  |  |
| `o3s1_2b_v11_b0/` | 4 | 0.5 MB |  |  |
| `o3s1_2b_v11_none/` | 4 | 0.4 MB |  |  |
| `o3s1_4b_rag_b0/` | 4 | 0.6 MB |  |  |
| `o3s1_4b_rag_oracle/` | 4 | 0.5 MB |  |  |
| `o3s1_4b_v11_b0/` | 4 | 0.4 MB |  |  |
| `o3s1_4b_v11_none/` | 4 | 0.3 MB |  |  |
| `o3s1sp_a_2b_rag_b0/` | 4 | 0.9 MB |  |  |
| `o3s1sp_a_2b_v11_b0/` | 4 | 0.7 MB |  |  |
| `o3s1sp_b_4b_rag_b0/` | 3 | 0.5 MB |  |  |
| `o3s1sp_b_4b_v11_b0/` | 4 | 0.5 MB |  |  |
| `o3s2_2b_rag_s2/` | 4 | 1.1 MB |  |  |
| `o3s2_2b_v12_s2/` | 4 | 0.6 MB |  |  |
| `o3s2_4b_rag_s2/` | 4 | 0.7 MB |  |  |
| `o3s2_4b_v12_s2/` | 4 | 0.4 MB |  |  |
| `o3s3_2b_rag_s3/` | 4 | 1.0 MB |  |  |
| `o3s3_2b_v12_s3/` | 4 | 0.5 MB |  |  |
| `o3s3_4b_rag_s3/` | 4 | 0.7 MB |  |  |
| `o3s3_4b_v12_s3/` | 4 | 0.4 MB |  |  |
| `o3s3g_2b_rag_guard/` | 4 | 1.1 MB |  |  |
| `o3s3g_2b_v12_guard/` | 4 | 0.5 MB |  |  |
| `o3s3g_4b_rag_guard/` | 4 | 0.7 MB |  |  |
| `o3s3g_4b_v12_guard/` | 4 | 0.4 MB |  |  |
| `o3s3p_2b_rag_s3/` | 4 | 0.3 MB |  |  |
| `o3s3sp_a_2b_rag_s3/` | 4 | 0.3 MB |  |  |
| `o3s3sp_a_2b_v12_s3/` | 4 | 0.2 MB |  |  |
| `o3s4_2b_rag_s4/` | 4 | 1.0 MB |  |  |
| `o3s4_2b_v12_s4/` | 4 | 0.4 MB |  |  |
| `o3s4_4b_rag_s4/` | 4 | 0.7 MB |  |  |
| `o3s4_4b_v12_s4/` | 4 | 0.4 MB |  |  |
| `o3s4sp_a_2b_rag_s4/` | 4 | 0.3 MB |  |  |
| `o3s4sp_a_2b_v12_s4/` | 3 | 0.2 MB |  |  |
| `o3s5_2b_rag_s5/` | 4 | 0.6 MB |  |  |
| `o3s5_2b_v12_s5/` | 4 | 0.3 MB |  |  |
| `o3s5_4b_rag_s5/` | 4 | 0.7 MB |  |  |
| `o3s5_4b_v12_s5/` | 4 | 0.3 MB |  |  |
| `o3s5h_2b_rag_ht/` | 4 | 1.0 MB |  |  |
| `o3s5h_2b_v12_ht/` | 4 | 0.4 MB |  |  |
| `o3s5h_4b_rag_ht/` | 4 | 0.7 MB |  |  |
| `o3s5h_4b_v12_ht/` | 4 | 0.3 MB |  |  |
| `o3s5sp_a_2b_rag_s5/` | 4 | 0.2 MB |  |  |
| `o3s5sp_a_2b_v12_s5/` | 4 | 0.1 MB |  |  |
| `o3s6_2b_rag_s6/` | 3 | 55.0 KB |  |  |
| `o3s6_2b_rag_s6m/` | 3 | 56.5 KB |  |  |
| `o3s6_2b_v12_s6/` | 3 | 97.2 KB |  |  |
| `o3s6_2b_v12_s6m/` | 3 | 0.1 MB |  |  |
| `o3s6_4b_rag_s6/` | 3 | 57.5 KB |  |  |
| `o3s6_4b_rag_s6m/` | 3 | 59.0 KB |  |  |
| `o3s6_4b_v12_s6/` | 3 | 99.9 KB |  |  |
| `o3s6_4b_v12_s6m/` | 3 | 0.1 MB |  |  |
| `o3s6c_2b_rag_s6/` | 3 | 51.3 KB |  |  |
| `o3s6c_2b_v12_s6/` | 3 | 0.1 MB |  |  |
| `o3s6c_4b_rag_s6/` | 3 | 51.6 KB |  |  |
| `o3s6c_4b_v12_s6/` | 3 | 0.1 MB |  |  |
| `o3s6d2_2b_s5h/` | 3 | 0.5 MB |  |  |
| `o3s6d2_2b_s6/` | 3 | 0.3 MB |  |  |
| `o3s6d2_4b_s5h/` | 3 | 0.5 MB |  |  |
| `o3s6d2_4b_s6/` | 3 | 0.3 MB |  |  |
| `o3s6d3_2b_s6/` | 3 | 0.3 MB |  |  |
| `o3s6d3_4b_s6/` | 3 | 0.3 MB |  |  |
| `o3s6d_2b_s5h/` | 3 | 0.5 MB |  |  |
| `o3s6d_2b_s6/` | 3 | 0.3 MB |  |  |
| `o3s6d_2b_s6m/` | 3 | 0.4 MB |  |  |
| `o3s6d_4b_s5h/` | 3 | 0.5 MB |  |  |
| `o3s6d_4b_s6/` | 3 | 0.3 MB |  |  |
| `o3s6d_4b_s6m/` | 3 | 0.4 MB |  |  |
| `o3s6dsp_a_2b_s5h/` | 3 | 0.6 MB |  |  |
| `o3s6dsp_a_2b_s6/` | 3 | 0.3 MB |  |  |
| `o3s6dsp_a_2b_s6m/` | 3 | 0.4 MB |  |  |
| `o3s7_2b_rag/` | 4 | 0.9 MB |  |  |
| `o3s7_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s7_4b_rag/` | 4 | 0.6 MB |  |  |
| `o3s7_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s7a_2b_rag/` | 4 | 1.0 MB |  |  |
| `o3s7a_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s7a_4b_rag/` | 4 | 0.6 MB |  |  |
| `o3s7a_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s7d_2b_s7/` | 3 | 0.3 MB |  |  |
| `o3s7d_4b_s7/` | 4 | 0.3 MB |  |  |
| `o3s8_2b_rag/` | 4 | 1.0 MB |  |  |
| `o3s8_2b_v12/` | 4 | 0.3 MB |  |  |
| `o3s8_4b_rag/` | 4 | 0.6 MB |  |  |
| `o3s8_4b_v12/` | 4 | 0.3 MB |  |  |
| `o3s8a_2b_rag/` | 4 | 0.9 MB |  |  |
| `o3s8a_4b_rag/` | 4 | 0.6 MB |  |  |
| `o3t_b0_2b_dlg/` | 4 | 0.9 MB |  |  |
| `o3t_b0_2b_fup/` | 4 | 0.4 MB |  |  |
| `o3t_b0_2b_rag/` | 4 | 3.4 MB |  |  |
| `o3t_b0_2b_v12/` | 4 | 1.7 MB |  |  |
| `o3t_b0_4b_dlg/` | 3 | 0.7 MB |  |  |
| `o3t_b0_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3t_b0_4b_rag/` | 4 | 2.2 MB |  |  |
| `o3t_b0_4b_v12/` | 4 | 1.3 MB |  |  |
| `o3t_final12_2b_fup/` | 3 | 0.2 MB |  |  |
| `o3t_final12_2b_rag/` | 4 | 2.6 MB |  |  |
| `o3t_final12_2b_v12/` | 4 | 0.8 MB |  |  |
| `o3t_final_2b_dlg/` | 3 | 0.4 MB |  |  |
| `o3t_final_2b_fup/` | 3 | 0.3 MB |  |  |
| `o3t_final_2b_rag/` | 4 | 2.9 MB |  |  |
| `o3t_final_2b_v12/` | 4 | 0.8 MB |  |  |
| `o3t_final_4b_dlg/` | 3 | 0.4 MB |  |  |
| `o3t_final_4b_fup/` | 4 | 0.3 MB |  |  |
| `o3t_final_4b_rag/` | 4 | 2.2 MB |  |  |
| `o3t_final_4b_v12/` | 4 | 0.9 MB |  |  |
| `o3tsp_a_2b_rag_b0/` | 4 | 0.6 MB |  |  |
| `o3tsp_a_2b_rag_final/` | 4 | 0.5 MB |  |  |
| `o3tsp_a_2b_v12_b0/` | 4 | 0.6 MB |  |  |
| `o3tsp_a_2b_v12_final/` | 4 | 0.3 MB |  |  |
| (files directly in `results_obj3/`) | 4 | 0.7 MB | | |

## `results_obj4/`

Objective 4: adapters (development-set comparisons, speed, decision).

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `_compare_step6/` | 3 | 0.1 MB |  | Paired dev comparison (Objective 3) |
| `_compare_step7/` | 3 | 0.2 MB |  | Paired dev comparison (Objective 3) |
| `_compare_step8/` | 3 | 66.3 KB |  | Paired dev comparison (Objective 3) |
| `_dialogues_step6/` | 3 | 52.2 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_dialogues_step7/` | 3 | 74.1 KB |  | Simulated discovery dialogues (Objective 3, Step 6) |
| `_step6/` | 2 | 11.7 KB |  |  |
| `_step7/` | 2 | 7.8 KB |  |  |
| `_step8/` | 2 | 3.1 KB |  |  |
| `o4s6_2b_base_dlg/` | 3 | 0.3 MB |  |  |
| `o4s6_2b_base_fup/` | 3 | 0.3 MB |  |  |
| `o4s6_2b_base_rag/` | 4 | 1.0 MB |  |  |
| `o4s6_2b_base_v12/` | 4 | 0.3 MB |  |  |
| `o4s6_2b_lora_dlg/` | 3 | 0.3 MB |  |  |
| `o4s6_2b_lora_fup/` | 3 | 0.2 MB |  |  |
| `o4s6_2b_lora_rag/` | 3 | 0.6 MB |  |  |
| `o4s6_2b_lora_v12/` | 4 | 0.3 MB |  |  |
| `o4s6_2b_qlora_dlg/` | 3 | 0.3 MB |  |  |
| `o4s6_2b_qlora_fup/` | 3 | 0.2 MB |  |  |
| `o4s6_2b_qlora_rag/` | 3 | 0.6 MB |  |  |
| `o4s6_2b_qlora_v12/` | 4 | 0.3 MB |  |  |
| `o4s6_4b_base_dlg/` | 3 | 0.3 MB |  |  |
| `o4s6_4b_base_fup/` | 3 | 0.3 MB |  |  |
| `o4s6_4b_base_rag/` | 3 | 0.7 MB |  |  |
| `o4s6_4b_base_v12/` | 4 | 0.3 MB |  |  |
| `o4s6_4b_lora_dlg/` | 3 | 0.3 MB |  |  |
| `o4s6_4b_lora_fup/` | 3 | 0.2 MB |  |  |
| `o4s6_4b_lora_rag/` | 3 | 0.6 MB |  |  |
| `o4s6_4b_lora_v12/` | 4 | 0.3 MB |  |  |
| `o4s7_2b_base_off_dlg/` | 3 | 0.3 MB |  |  |
| `o4s7_2b_base_off_fup/` | 3 | 0.3 MB |  |  |
| `o4s7_2b_base_off_rag/` | 4 | 0.9 MB |  |  |
| `o4s7_2b_base_off_v12/` | 4 | 0.3 MB |  |  |
| `o4s7_2b_lora_off_dlg/` | 3 | 0.3 MB |  |  |
| `o4s7_2b_lora_off_fup/` | 3 | 0.2 MB |  |  |
| `o4s7_2b_lora_off_rag/` | 3 | 0.6 MB |  |  |
| `o4s7_2b_lora_off_v12/` | 4 | 0.3 MB |  |  |
| `o4s7_4b_base_short_dlg/` | 3 | 0.3 MB |  |  |
| `o4s7_4b_base_short_fup/` | 3 | 0.3 MB |  |  |
| `o4s7_4b_base_short_rag/` | 4 | 0.7 MB |  |  |
| `o4s7_4b_base_short_v12/` | 4 | 0.3 MB |  |  |
| `o4s7_4b_lora_short_dlg/` | 3 | 0.3 MB |  |  |
| `o4s7_4b_lora_short_fup/` | 3 | 0.2 MB |  |  |
| `o4s7_4b_lora_short_rag/` | 3 | 0.6 MB |  |  |
| `o4s7_4b_lora_short_v12/` | 4 | 0.3 MB |  |  |
| `o4s7_4b_lora_shortoff_dlg/` | 3 | 0.3 MB |  |  |
| `o4s7_4b_lora_shortoff_fup/` | 3 | 0.2 MB |  |  |
| `o4s7_4b_lora_shortoff_rag/` | 3 | 0.6 MB |  |  |
| `o4s7_4b_lora_shortoff_v12/` | 4 | 0.3 MB |  |  |
| `o4s8_2b_base_rag/` | 4 | 0.5 MB |  |  |
| `o4s8_2b_base_v12/` | 4 | 0.2 MB |  |  |
| `o4s8_2b_lora_off_rag/` | 3 | 0.3 MB |  |  |
| `o4s8_2b_lora_off_v12/` | 4 | 0.2 MB |  |  |
| `o4s8_2b_lora_rag/` | 3 | 0.3 MB |  |  |
| `o4s8_2b_lora_v12/` | 4 | 0.2 MB |  |  |

## `results_o4/`

Objective 4: training trajectories and adapter runs.

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `o4traj_a_followups/` | 4 | 1.3 MB |  |  |
| `o4traj_a_store/` | 4 | 5.8 MB |  |  |
| `o4traj_a_tools/` | 4 | 2.2 MB |  |  |
| `o4traj_b_followups/` | 4 | 1.3 MB |  |  |
| `o4traj_b_store/` | 4 | 5.8 MB |  |  |
| `o4traj_b_tools/` | 4 | 2.2 MB |  |  |
| `traj_a/` | 3 | 25.1 MB |  |  |
| `traj_b/` | 3 | 24.8 MB |  |  |

## `results_obj5/`

Objective 5: the app (parity, stages, streaming, images, measurement, walkthroughs).

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `_a11y_step5/` | 2 | 3.3 KB |  | Objective 5, Step 5: accessibility scan |
| `_app_step4/` | 4 | 8.3 KB |  |  |
| `_cache/` | 1 | 1.7 MB |  |  |
| `_compare_step6/` | 2 | 2.4 KB |  | Objective 5, Step 6: compare mode against single runs |
| `_images_step7/` | 4 | 87.3 KB |  |  |
| `_measure_step8/` | 10 | 0.3 MB |  | Objective 5, Step 8: in-place measurement (app and harness, same cases, alternating) |
| `_parity_step2/` | 2 | 1.6 KB |  | Step 2: shared engine against the harness's own code |
| `_stages_step3/` | 2 | 2.2 KB |  | Step 3: per-stage logs and the stage clock's cost |
| `_stream_step4/` | 2 | 1.2 KB |  | Objective 5, Step 4: streamed against non-streamed replies |
| `_walkthrough_step9/` | 29 | 0.3 MB |  | Objective 5, Step 9: walkthrough of the design scenarios |
| `o5s2_2b_dlg_core/` | 3 | 97.9 KB |  |  |
| `o5s2_2b_dlg_legacy/` | 3 | 75.1 KB |  |  |
| `o5s2_2b_rag_core/` | 4 | 0.4 MB |  |  |
| `o5s2_2b_rag_legacy/` | 4 | 0.3 MB |  |  |
| `o5s2_2b_v12_core/` | 4 | 0.2 MB |  |  |
| `o5s2_2b_v12_legacy/` | 4 | 0.1 MB |  |  |
| `o5s2_4b_dlg_core/` | 3 | 0.1 MB |  |  |
| `o5s2_4b_dlg_legacy/` | 3 | 77.2 KB |  |  |
| `o5s2_4b_rag_core/` | 3 | 0.2 MB |  |  |
| `o5s2_4b_rag_legacy/` | 3 | 0.2 MB |  |  |
| `o5s2_4b_v12_core/` | 4 | 0.2 MB |  |  |
| `o5s2_4b_v12_legacy/` | 4 | 0.1 MB |  |  |
| `o5s3_2b_rag_off/` | 4 | 0.5 MB |  |  |
| `o5s3_2b_rag_on/` | 4 | 0.7 MB |  |  |
| `o5s3_2b_rag_seq/` | 3 | 86.9 KB |  |  |
| `o5s3_2b_v12_off/` | 4 | 0.2 MB |  |  |
| `o5s3_2b_v12_on/` | 4 | 0.3 MB |  |  |
| `o5s3_2b_v12_seq/` | 3 | 52.2 KB |  |  |
| `o5s4_2b_v12_stream/` | 4 | 0.2 MB |  |  |
| `o5s4_4b_v12_stream/` | 4 | 0.2 MB |  |  |
| `o5s7_2b_img_dev/` | 3 | 0.1 MB |  |  |
| `o5s7_2b_img_test/` | 3 | 0.1 MB |  |  |
| `o5s7_4b_img_dev/` | 3 | 0.1 MB |  |  |
| `o5s7_4b_img_test/` | 3 | 0.1 MB |  |  |

## `kaggle/_pulled/`

Kaggle jobs: the log and returned files of every job.

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `o4_step5/` | 3 | 20.6 KB | 1 |  |
| `o4_step5_smoke/` | 3 | 74.1 KB | 1 |  |
| `o4_step5_smoke_4b/` | 4 | 36.7 MB |  |  |
| `o4_teacher/` | 4 | 0.1 MB |  |  |
| `o4_teacher_pilot/` | 4 | 10.2 KB |  |  |
| `o4_teacher_retry/` | 4 | 0.2 MB |  |  |
| `o4_train/` | 3 | 0.4 MB | 1 |  |
| `o4_train_smoke/` | 3 | 69.3 KB | 1 |  |
| `plan_o3g_01_r6/` | 4 | 0.3 MB |  |  |
| `plan_o3g_02_b0/` | 4 | 1.7 MB |  |  |
| `plan_o3g_03_r5/` | 4 | 1.3 MB |  |  |
| `plan_o3g_04_r4/` | 4 | 1.3 MB |  |  |
| `plan_o3g_05_r3/` | 4 | 1.3 MB |  |  |
| `plan_o3g_06_r2/` | 4 | 1.5 MB |  |  |
| `plan_o3g_07_r1/` | 4 | 1.6 MB |  |  |
| `plan_o3g_08_nr/` | 4 | 0.6 MB |  |  |
| `plan_o3gs/` | 3 | 0.1 MB | 1 |  |
| `plan_o3l_01_r6_2b_rag/` | 4 | 0.4 MB |  |  |
| `plan_o3l_02_r6_4b_rag/` | 4 | 0.4 MB |  |  |
| `plan_o3l_03_r6_2b_rest/` | 4 | 0.2 MB |  |  |
| `plan_o3l_04_r6_4b_rest/` | 4 | 0.3 MB |  |  |
| `plan_o3l_05_b0_2b_rag/` | 4 | 0.6 MB |  |  |
| `plan_o3l_06_b0_4b_rag/` | 4 | 0.4 MB |  |  |
| `plan_o3l_07_b0_2b_rest/` | 4 | 0.5 MB |  |  |
| `plan_o3l_08_b0_4b_rest/` | 4 | 0.4 MB |  |  |
| `plan_o3l_09_ref_2b_all/` | 4 | 0.6 MB |  |  |
| `plan_o3l_10_ref_4b_all/` | 4 | 0.5 MB |  |  |
| `plan_o3l_11_r5_2b_rag/` | 4 | 0.5 MB |  |  |
| `plan_o3l_12_r5_4b_rag/` | 4 | 0.4 MB |  |  |
| `plan_o3ls_2b/` | 4 | 67.3 KB |  |  |
| `plan_o3ls_4b/` | 4 | 37.7 KB |  |  |
| `selftest/` | 4 | 57.0 KB |  |  |
| `step9_train/` | 3 | 23.8 KB | 1 |  |

## `logs/`

Run-time logs of the app, llama-server and the kiosk launcher.

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `app/` | 770 | 4.3 MB |  |  |
| `lab/` | 2 | 4.3 KB |  |  |
| `server/` | 1 | 1.9 MB |  |  |

## `finetune/`

Objective 4: training data, examples, plans and training outputs.

| Folder | Files here | Size here | On Drive | Starts with |
|---|---:|---:|---:|---|
| `adapters/` | 36 | 120.1 MB | 6 |  |
| `examples/` | 7 | 43.4 MB |  |  |
| `knowledge/` | 2 | 1.1 MB |  |  |
| `plans/` | 2 | 9.8 KB |  |  |
| `teacher/` | 4 | 1.2 MB |  |  |
| `train/` | 4 | 2.4 MB |  |  |
| (files directly in `finetune/`) | 22 | 0.2 MB | | |


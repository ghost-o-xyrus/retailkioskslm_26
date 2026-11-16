# Judging instructions (Objective 3, Step 15)

You will read items from a watch-store kiosk assistant. Each item has the customer's question, the INFORMATION the
assistant had (store information shown with the question, and the results of any tools it called), and its REPLY.
Judge only from the information shown. You don't know the store beyond it.

Give each item exactly one label:

- **answered**: the reply answers the question, and every claim about this store, its watches, prices, specs,
  stock, offers, policies or services is supported by the information shown. A correct "no" or "not listed" that
  the information supports (for example "there is no green dial variant") is answered.
- **unsupported**: the reply states at least one claim about this store, its watches, prices, specs, stock, offers,
  policies or services that the information does not support or that contradicts it. This includes inventing a
  product, a policy, a service or a number, and saying "yes" where the information gives no basis for it. Mark this
  even if the rest of the reply is right, or if it also offers a staff member.
- **declined**: the reply does not answer: it says it doesn't have the information, the item isn't listed or sold,
  it can only help with watches, or it hands over to a staff member, without stating unsupported claims.

General watch knowledge (what a chronograph is, how to care for leather) is not a claim about the store. Count it as
unsupported only if it contradicts the information shown or is plainly false. Ignore tone, length and language
(English, Hindi or Hinglish replies are all fine). A promise that a staff member has been called is not a claim to
check.

Return a JSON list, one object per item, in the same order: [{"item": "J0001", "label": "answered"}, ...]. You can
add a short "note" for any item that was hard to call.

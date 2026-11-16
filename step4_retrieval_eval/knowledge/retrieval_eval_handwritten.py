"""
Hand-written questions for the retrieval eval (Objective 2, Step 4).

Each answerable entry is (gold chunk id, question, facts). `facts` is a list of groups; every group must be
matched by at least one of its strings. Facts are checked against the gold chunk text, so a typo in a label
fails the build instead of silently mis-scoring.
Questions are phrased the way a customer would ask, not copied from the FAQ wording.
"""

NEG = ["no", "not", "doesn't", "does not", "don't", "do not", "only", "nahi", "nahin"]

FAQ = [
    ("faq:what-are-the-store-hours", "When do you close tonight?", [["22:00", "10 pm", "10:00 pm"]]),
    ("faq:which-payment-methods-are-accepted", "Can I pay with Google Pay or UPI here?", [["UPI"]]),
    ("faq:do-you-offer-gift-wrapping", "It's a present. Will you wrap it for me?", [["gift wrapping", "wrap"]]),
    ("faq:can-i-get-a-watch-engraved", "Can you write my husband's initials on the back of the watch?", [["Rs. 500", "500"], ["2 days"]]),
    ("faq:can-i-try-a-watch-on", "Am I allowed to put one on before buying?", [["staff member"]]),
    ("faq:can-you-hold-a-watch-for-me", "Could you keep a watch aside until I come back with my wife?", [["24 hours"]]),
    ("faq:can-you-transfer-a-watch-from-another-store", "If this store doesn't have it, can you get it from another branch?", [["1 to 2 days"]]),
    ("faq:do-you-deliver", "Can you send the watch to my house?", [["1 to 3 days"], ["2,000"]]),
    ("faq:do-you-buy-or-exchange-old-watches", "Can I trade in my old watch for a new one?", [["exchange"], ["Atelier"]]),
    ("faq:are-prices-inclusive-of-gst", "Is tax already included in the price shown?", [["18%"]]),
    ("faq:which-emi-tenures-are-available", "Can I pay in instalments over six months?", [["3 or 6 months"]]),
    ("faq:can-i-pay-partly-in-cash-and-partly-by-card", "Can I split the payment between cash and my debit card?", [["split"]]),
    ("faq:do-i-get-a-printed-or-digital-invoice", "Will you email me the bill?", [["SMS and email", "email"]]),
    ("faq:i-lost-my-invoice-can-i-get-a-copy", "I can't find the receipt from when I bought my watch. What can I do?", [["reprint"]]),
    ("faq:what-does-pre-booking-mean", "How does booking a watch before it launches work?", [["token"], ["Rs. 500", "500"]]),
    ("faq:can-i-reserve-a-watch-online-and-pick-it-up-here", "Can I book a watch on the website and collect it at this store?", [["Reserve-and-collect", "reserve"], ["24 hours"]]),
    ("faq:can-i-be-told-when-an-out-of-stock-watch-arrives", "The one I want is sold out. Can you let me know when it's back?", [["SMS"]]),
    ("faq:do-you-sell-gift-cards", "Do you have vouchers I could give as a present?", [["gift cards"], ["12 months"]]),
    ("faq:can-a-gift-card-be-used-with-a-festive-offer", "If I pay with a gift card, do I still get the festive discount?", [["any current offer", "current offer"]]),
    ("faq:does-every-watch-come-with-a-box", "Will the watch come in a nice box?", [["wooden presentation box", "gift box"]]),
    ("faq:can-i-get-a-gift-receipt-without-the-price", "Can I get a bill that doesn't show how much I paid?", [["gift receipt"]]),
    ("faq:can-the-person-i-gift-it-to-exchange-it", "If my brother doesn't like the watch I give him, can he swap it?", [["7-day", "7 day"]]),
    ("faq:how-do-i-know-which-case-size-suits-me", "My wrist is quite thin. What size watch should I look at?", [["15 cm"]]),
    ("faq:can-a-metal-bracelet-be-shortened", "The steel strap is too loose. Can you remove some links?", [["10 to 15 minutes"]]),
    ("faq:can-a-bracelet-be-made-longer", "My bracelet is too tight. Can you add links?", [["Spare links", "spare links"], ["5 to 7 days"]]),
    ("faq:can-i-swap-a-leather-strap-for-a-metal-bracelet", "Can I put a steel bracelet on my leather-strap watch?", [["designed for both"]]),
    ("faq:what-is-lug-width", "What does lug width mean when buying a strap?", [["distance between the two lugs", "lugs"]]),
    ("faq:how-long-does-a-battery-last", "How often will I need to change the battery?", [["2 to 3 years"]]),
    ("faq:how-do-i-know-the-battery-is-low", "My second hand is jumping every few seconds. Is something wrong?", [["2- or 4-second", "battery"]]),
    ("faq:do-you-replace-batteries-in-other-brands-watches", "Can you put a new battery in a watch I didn't buy from Veyra?", [["other brands", "non-Veyra"]]),
    ("faq:how-long-does-a-solar-watch-run-in-the-dark", "If I keep my solar watch in a drawer, how long will it keep going?", [["6 months"]]),
    ("faq:how-long-does-an-automatic-run-when-i-take-it-off", "My automatic stopped overnight on the table. How long does it run off the wrist?", [["40 hours"]]),
    ("faq:do-automatic-watches-need-a-battery", "Does a self-winding watch have a battery inside?", [["No"]]),
    ("faq:how-do-i-set-the-date-safely", "Is there a wrong time of day to change the date?", [["9 pm and 3 am"]]),
    ("faq:what-is-a-screw-down-crown", "Why does the winding knob on my diver screw in?", [["screws into the case", "keep water out"]]),
    ("faq:how-do-i-use-a-chronograph", "How do I start and stop the stopwatch on my watch?", [["top pusher"]]),
    ("faq:how-do-i-set-the-alarm-on-a-digital-watch", "How do I make my digital watch beep in the morning?", [["alarm"], ["mode button"]]),
    ("faq:does-the-backlight-drain-the-battery", "Does using the light on my digital watch use up the battery?", [["backlight"]]),
    ("faq:what-does-dual-time-mean", "What does it mean when a watch shows two time zones?", [["second time zone"]]),
    ("faq:why-does-my-watch-gain-or-lose-a-few-seconds", "My watch is a few seconds off after a month. Is that normal?", [["15 seconds a month"]]),
    ("faq:can-i-wear-my-watch-in-the-gym", "Is it okay to work out with my watch on?", [["sweating"]]),
    ("faq:can-i-wear-my-watch-in-a-sauna-or-hot-shower", "Can I keep my watch on in the steam room?", [["seals"]]),
    ("faq:how-should-i-store-a-watch-i-don-t-wear-often", "Where should I keep a watch I only wear on special occasions?", [["box"], ["magnets"]]),
    ("faq:why-has-my-leather-strap-changed-colour", "Why has my brown strap gone darker?", [["skin oils", "darkens"]]),
    ("faq:is-the-plating-on-gold-tone-watches-permanent", "Will the gold colour on my watch fade?", [["plated"]]),
    ("faq:do-i-need-to-register-my-watch-for-the-warranty", "Do I have to sign up somewhere to activate the warranty?", [["invoice date", "automatically"]]),
    ("faq:i-lost-the-warranty-card-is-my-warranty-still-valid", "I threw away the warranty card. Am I still covered?", [["invoice alone"]]),
    ("faq:can-i-claim-warranty-at-another-veyra-store", "I bought it in another city. Can I get it repaired under warranty here?", [["any Veyra brand store"]]),
    ("faq:does-a-battery-replacement-affect-the-warranty", "If I change the battery at a local shop, do I lose the warranty?", [["void"]]),
    ("faq:how-long-does-a-repair-take", "How many days will a warranty repair take?", [["7 working days"]]),
    ("faq:can-i-track-my-repair", "How will I know when my watch is ready after a repair?", [["job card", "SMS"]]),
    ("faq:is-there-parking-at-central-mall", "Where can I park my scooter?", [["parking"]]),
    ("faq:is-the-store-wheelchair-accessible", "My father uses a wheelchair. Can he get into the store?", [["step-free"]]),
    ("faq:can-i-use-the-kiosk-to-find-a-watch-and-then-see-it", "Can this screen get someone to bring me the watch I found?", [["call a staff"]]),
    ("faq:which-other-veyra-stores-are-nearby", "Is there another Veyra shop close by?", [["Station Road"]]),
]

POLICY = [
    ("policy:warranty", "How long is the warranty on a Veyra Pulse watch?", [["12 months"]]),
    ("policy:warranty", "Is a broken strap covered by warranty?", [["straps and bracelets"]]),
    ("policy:warranty", "The glass on my watch cracked. Will warranty pay for it?", [["glass breakage"]]),
    ("policy:warranty", "Can my wife claim warranty on a watch I bought her?", [["gift recipient"]]),
    ("policy:returns", "Can I get my money back if I don't like the watch?", [["Refunds", "refund"]]),
    ("policy:returns", "I bought it on sale. Can I return it?", [["exchanged but not refunded"]]),
    ("policy:returns", "How long do I have to return a watch I ordered online?", [["15 days"]]),
    ("policy:returns", "Can I exchange a watch I had engraved?", [["Engraved watches"]]),
    ("policy:service", "How much does it cost to replace a cracked mineral glass?", [["Rs. 500 to Rs. 900"]]),
    ("policy:service", "How long does servicing an automatic movement take?", [["3 to 4 weeks"]]),
    ("policy:service", "How often should an automatic watch be serviced?", [["4 to 5 years"]]),
    ("policy:service", "What does a water-resistance test cost?", [["Rs. 400"]]),
    ("policy:care#what-the-water-resistance-rating-means", "Can I swim in the pool with a 50 m watch?", [["light swimming"]]),
    ("policy:care#what-the-water-resistance-rating-means", "Is a 30 m watch fine in the shower?", [["Showering, swimming"]]),
    ("policy:care#what-the-water-resistance-rating-means", "Which rating do I need for scuba diving?", [["200 m"]]),
    ("policy:care#everyday-care", "Can a magnet stop my watch?", [["magnets"]]),
    ("policy:care#everyday-care", "How do I clean my watch after the beach?", [["fresh water"]]),
    ("policy:size_guide#children", "What kind of watch suits a 5-year-old?", [["learning dial"]]),
    ("policy:size_guide#case-thickness", "I want a watch thin enough to fit under my shirt cuff.", [["shirt cuff"]]),
    ("policy:size_guide#measuring-your-wrist", "How do I measure my wrist at home?", [["strip of paper"]]),
    ("policy:brand#sub-brands", "What is Veyra Nitya?", [["value"]]),
    ("policy:brand#sub-brands", "Which Veyra range is for students and young people?", [["Veyra Pulse"]]),
]

GLOSSARY = [
    ("glossary:analog", "What's the difference between an analog watch and others?"),
    ("glossary:digital", "What do you call a watch that shows the time as numbers?"),
    ("glossary:ana-digi", "What is an ana-digi watch?"),
    ("glossary:quartz", "What does quartz movement mean?"),
    ("glossary:automatic", "How does a self-winding watch work?"),
    ("glossary:solar", "How does a light-powered watch get its energy?"),
    ("glossary:chronograph", "What's a chronograph?"),
    ("glossary:multifunction", "What are the small dials on a multifunction watch for?"),
    ("glossary:day-date", "What is a day-date watch?"),
    ("glossary:moonphase", "What's that little window that shows the moon?"),
    ("glossary:small-seconds", "Why does the seconds hand sit on its own tiny dial?"),
    ("glossary:open-heart", "What is an open-heart dial?"),
    ("glossary:sapphire-crystal", "Is sapphire glass better at resisting scratches?"),
    ("glossary:mineral-glass", "What kind of glass is mineral glass?"),
    ("glossary:acrylic-glass", "Can scratches on acrylic glass be removed?"),
    ("glossary:atm-bar", "What does 5 ATM mean on the back of a watch?"),
    ("glossary:lume", "What makes the hands glow at night?"),
    ("glossary:316l-stainless-steel", "What is 316L steel?"),
    ("glossary:titanium", "Why are titanium watches so light?"),
    ("glossary:tonneau", "What does a tonneau-shaped case look like?"),
    ("glossary:bezel", "What does the turning ring around a dive watch do?"),
    ("glossary:crown", "What is the knob on the side of a watch called?"),
    ("glossary:lugs", "What are the lugs on a watch?"),
    ("glossary:mesh-strap", "What is a mesh strap made of?"),
    ("glossary:fkm-rubber", "What is FKM rubber?"),
]

OFFERS = [
    ("offer:PR-FEST10", "Is there any festive discount on Veyra watches right now?", [["10%"]]),
    ("offer:PR-PULSE300", "Any deal on Pulse watches this month?", [["300"]]),
    ("offer:PR-SHAGUN15", "Is the Shagun range on offer for the wedding season?", [["15%"]]),
    ("offer:PR-EXCH500", "Do I get anything off an Atelier watch if I give you my old one?", [["500"]]),
    ("offer:PR-MONSOON20", "Is the monsoon sale on Nitya still running?", [["expired"]]),
    ("offer:PR-KIDSDAY", "Is there a Children's Day offer on kids' watches?", [["1,499"]]),
    ("offer:PR-FEST10", "What's the maximum discount I can get in the festive sale?", [["1,500"]]),
    ("offer:PR-EXCH500", "Can the old-watch exchange be combined with other offers?", [["yes"]]),
]

STORES = [
    ("store:ST02", "What time does the Station Road store open?", [["10:30"]]),
    ("store:ST03", "How far is the City Centre Mall store from here?", [["6.8 km"]]),
    ("store:ST04", "Is Time Square a Veyra store or a multi-brand shop?", [["partner outlet"]]),
    ("store:ST05", "Can I visit your warehouse to pick up a watch?", [["no walk-in"]]),
    ("store:ST01", "Until what time is this Central Mall store open?", [["22:00"]]),
    ("store:ST03", "When does the City Centre Mall shop close?", [["22:00"]]),
]

HINGLISH = [
    ("faq:what-are-the-store-hours", "Store kitne baje band hota hai?", [["22:00"]]),
    ("faq:which-emi-tenures-are-available", "Kya main EMI pe le sakta hoon?", [["EMI"]]),
    ("faq:can-you-hold-a-watch-for-me", "Kya aap ye watch kal tak mere liye rakh sakte ho?", [["24 hours"]]),
    ("faq:do-you-deliver", "Kya aap ghar pe delivery karte ho?", [["1 to 3 days"]]),
    ("faq:can-i-get-a-watch-engraved", "Watch ke peeche naam likhwa sakte hain kya?", [["Rs. 500", "500"]]),
    ("faq:are-prices-inclusive-of-gst", "Kya price mein GST shaamil hai?", [["18%"]]),
    ("faq:do-you-sell-gift-cards", "Gift card milta hai kya?", [["gift cards"]]),
    ("faq:how-long-does-a-battery-last", "Battery kitne saal chalti hai?", [["2 to 3 years"]]),
    ("faq:can-a-metal-bracelet-be-shortened", "Chain thodi chhoti karwa sakte hain?", [["10 to 15 minutes"]]),
    ("faq:can-i-wear-my-watch-in-the-gym", "Gym mein watch pehen sakte hain kya?", [["sweating"]]),
    ("faq:is-there-parking-at-central-mall", "Mall mein parking hai kya?", [["parking"]]),
    ("faq:does-every-watch-come-with-a-box", "Watch ke saath dabba milega?", [["box"]]),
    ("faq:i-lost-the-warranty-card-is-my-warranty-still-valid", "Warranty card kho gaya, warranty abhi bhi chalegi?", [["invoice alone"]]),
    ("policy:returns", "Pasand nahi aaya toh exchange ho jayega?", [["7 days"]]),
    ("policy:warranty", "Pulse watch pe kitni warranty hai?", [["12 months"]]),
    ("policy:service", "Battery badalne ka kitna lagega?", [["Rs. 250 to Rs. 450"]]),
    ("policy:care#what-the-water-resistance-rating-means", "50 metre wali watch se swimming kar sakte hain?", [["light swimming"]]),
    ("offer:PR-SHAGUN15", "Shagun watches pe koi offer chal raha hai?", [["15%"]]),
    ("store:ST02", "Station Road wala store kitne baje khulta hai?", [["10:30"]]),
    ("glossary:chronograph", "Chronograph ka matlab kya hota hai?", []),
]

# ---- Unanswerable: nothing in the corpus answers these ----
NOT_SOLD = [
    "Do you have any Rolex watches?", "Do you sell Casio G-Shock?", "I'm looking for an Apple Watch.",
    "Do you have a smartwatch that tracks my heart rate?", "Do you sell fitness bands?", "Can I buy a wall clock here?",
    "Do you have pocket watches?", "Do you sell sunglasses?", "Do you have a smart ring?", "Do you sell perfume?",
    "Is the Omega Seamaster available?", "Do you have any solid gold watches?", "Do you sell diamond jewellery?",
    "Do you have an alarm clock for my bedside?", "Do you sell watch winders?", "Do you have a GPS running watch?",
    "Do you sell Fossil watches?", "Do you have a watch with a heart-rate sensor?", "Do you sell leather wallets?",
    "Do you have wooden watches?",
]

OFF_TOPIC = [
    "What's the weather like today?", "Who won the cricket match yesterday?", "Can you recommend a good restaurant?",
    "What time does the cinema start?", "How do I get to the railway station?", "Tell me a joke.",
    "What's the price of petrol today?", "Can you help me with my maths homework?", "What's the Wi-Fi password?",
    "Where is the nearest ATM?", "Book me a taxi.", "Who is the prime minister?",
]

MISSING_POLICY = [
    "Do you ship watches to Singapore?", "Is there a student discount?", "Can I pay with a foreign credit card?",
    "Who designs Veyra watches?", "Do you have a store in Mumbai?", "Do you price-match other shops?",
    "Can you print my company logo on the dial?", "Do you offer corporate bulk discounts?",
    "Can I get same-day delivery?", "Is there a loyalty points programme?", "Who is the CEO of Veyra?",
    "Do you offer a home try-on service?", "Can I rent a watch for a wedding?", "Do you have a store in Dubai?",
    "Can I order a watch that isn't in your catalogue?",
]

MISSING_ATTRIBUTE = [
    ("weight", "How much does the {name} weigh?"),
    ("lug width", "What is the lug width of the {name}?"),
    ("battery model", "Which battery model does the {name} take?"),
    ("clasp", "What kind of clasp does the {name} have?"),
    ("caseback", "Does the {name} have a see-through caseback?"),
    ("coating", "Does the glass on the {name} have an anti-reflective coating?"),
    ("strap length", "How long is the strap on the {name}?"),
]

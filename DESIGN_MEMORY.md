# Personal-site design and editorial memory

Consult this file before changing site copy, article presentation or imagery.
Record owner feedback separately from editorial interpretations. Preserve later
reversals rather than treating a rejected draft as an approved style reference.

## 12 October 2026 — explicit AI-slop rejection

Rejected opening: “You ask an AI a question and it starts typing. Then you wait.”
The owner called this “AI slop trash writing.”

Practical rule: no canned second-person chatbot scenes or staged waiting and
frustration as a technical article hook. Start with the mechanism, constraint or
result. Vary sentence length around actual meaning; empty fragments are filler,
not cadence. Do not treat this rejected opening as evidence of the owner's voice.

## 12 October 2026 — related technical-level correction

The owner rejected “Helping AI write faster” as too layman, said readers already
know token-by-token generation is the bottleneck, and requested “a tad more
technical.” This is a title/audience correction, distinct from the explicit
AI-slop rejection above.

Practical rule: name the specific mechanism or contribution in the title. Assume
basic familiarity with LLM token generation. Explain what is distinctive about
the method without restarting at definitions of tokens or GPUs. Keep concrete
examples and clear prose; the request does not justify unnecessary jargon.

## Established preferences

- Use the owner's 2018–2021 personal technical posts as voice references, while
  improving their flow and avoiding repeated explanations or invented anecdotes.
- No fluff added merely to create variety in sentence length.
- One meaningful heading, without a decorative eyebrow or redundant caption.
- Follow the existing brand and actual owner references. Do not use Impeccable
  by default or substitute another generic design skill.

Source: owner messages in this personal-site chat on 12 October 2026. Detailed
writing references are in `content/jacobi-forcing/voice-notes.txt`.

## 12 October 2026 — motion-video preference

The owner asked for the motion video to be clearer and more powerful for
marketing, and confirmed that 30 seconds is fine if it opens with a hook.
This is a marketing-format preference, not an explicit AI-slop example.

Editorial application: put the concrete result on screen immediately, make the
training contribution visible, and retain the benchmark scope and quality
tradeoff. Use a readable article destination at the end. Keep each explanation
visually distinct and avoid a long introduction to the familiar serial bottleneck.

## 12 October 2026 — video-hook correction

The owner rejected the “3.97× decoding throughput” opening: a plain statistic
and title card did not earn attention. This is a hook and design correction;
the owner did not explicitly label it AI slop.

The earlier editorial application of putting the result on screen immediately
is superseded as the opening strategy. It remains above as a record of the
rejected interpretation, not an approved reference for future hooks.

Superseded assistant interpretation: open on the measured contradiction, “Parallel
decoding made this LLM slower.” Show the original autoregressive model at
41.3 tokens/s beside plain Jacobi decoding at 39.9 tokens/s, scoped to the
reported HumanEval setup. Explain why parallel predictions can fail to survive
verification, then show how training addresses that problem before revealing
the later 3.97× payoff. Keep the benchmark scope and accuracy tradeoff visible
with the result. The hook should create a specific technical question that the
film answers, rather than relying on a large number or title treatment alone.
The owner subsequently rejected this direction; it is not an owner preference.

## 12 October 2026 — owner restores the article's intended hook

The owner corrected the contradiction-led interpretation: “OUR ARTICLE HOOK IS
ABOUT WHAT IF MODELS COULD GENERATE MULTIPLE TOKENS AT A TIME NOT THE SHIT YOU
ARE SAYING”. The prior “Parallel decoding made this LLM slower” direction was
an assistant interpretation and is rejected. Do not reuse it as the hook or
attribute it to the owner.

Current intended opening: “What if LLMs could generate multiple tokens at once?”
The owner's premise controls the video. Visually, the same serial token tile
becomes a parallel block; the film then explains how training makes this useful.
The scoped benchmark result and accuracy tradeoff come later as the payoff.
Do not replace this premise with a statistic, a contradiction, or another
assistant-invented framing.

## 12 October 2026 — extend the hook to article packaging

The owner asked for the article title and cover image to use the same hook.
The current article headline and dominant cover lettering are now “What if LLMs
could generate multiple tokens at once?” Keep this question consistent across
the article, homepage feature, blog index, feed and social previews. Retain LLM
and token terminology; the earlier instruction to name the method in the title
is superseded by this explicit question-led packaging request. The technical
article body and evidence remain unchanged.


## 13 October 2026 — restore the baseline in the introduction

The owner noted that the familiar token-by-token autoregressive generation
baseline had been lost. They want the introduction to establish that commonly
understood approach and present parallel generation as its alternative.
Practical rule: acknowledge the baseline in one direct sentence, then move to
parallel token prediction and the training contribution. Assuming familiarity
does not mean removing the comparison that motivates the article. This does
not reverse the rejection of canned chatbot scenes or staged waiting.


## 13 October 2026 — meaningful media in the website’s house style

The owner asked to redo the article cover and video in the website’s house
style, and said the old image was meaningless. This is a grounded usefulness
and brand correction, not an explicit AI-slop label. Use the homepage’s dark
teal, cream, mint, sky blue and yellow with Host Grotesk and rounded geometry.
Show a serial token chain versus grouped parallel guesses, including refinement
and verification. Do not reuse abstract 3D token sculptures as the explanation.
Preserve the exact multiple-token hook, the restored baseline intro, and the
video’s distinction between guesses, committed prefixes and measured results.

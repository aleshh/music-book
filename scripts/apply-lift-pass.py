#!/usr/bin/env python3

"""Apply the approved one-sentence lift pass to numbered manuscript pieces.

The sentence map makes the editorial choices auditable. The script is
idempotent: an existing lift sentence is not inserted a second time.
"""

from __future__ import annotations

import re
import textwrap
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CHAPTER_DIR = PROJECT_ROOT / "chapters"
NUMBERED_HEADING = re.compile(r"^## (\d+)\. ")

LIFT_SENTENCES = {
    1: "It can be invited, redirected, and renewed.",
    2: "Change the surrounding field, and the same sound can pass from atmosphere to event without changing a note.",
    3: "The question turns prominence from an effect to chase into a relation you can shape.",
    4: "The opportunity is not to control every response, but to design a frame in which more than one kind of attention can remain musically alive.",
    5: "Once you know that cost, you can decide where a listener must stay and where the music will keep a place for their return.",
    6: "This gives form another dimension: not only what changes, but how strongly each change asks to be witnessed.",
    7: "A piece can grow larger in the ear without adding a single layer; it need only make more of its existing relations available.",
    8: "A passage can renew itself without acquiring new material. It can give the material already present a new responsibility.",
    9: "Supporting several possible hearings can make a piece more exact, not less: each one must be carried by something the music actually does.",
    10: "Answering them can free the music from constant insistence and concentrate its force where continuous witness really matters.",
    11: "Once located, that demand becomes material you can strengthen, soften, or move.",
    12: "That is an enlargement of composition, not a surrender of it.",
    13: "Once we hear those clocks separately, duration becomes something we can shape rather than merely endure.",
    14: "A long work earns its scale when small relations begin to do work that shorter time could not give them.",
    15: "Choose the clock, and slowness becomes a compositional action rather than a number.",
    16: "The surrounding clock can become counterpoint, resistance, or part of the score.",
    17: "The gain is more precise than timelessness: a composer can loosen direction without pretending time has disappeared.",
    18: "Give the silence something to transform, and waiting becomes an event the listener can enter.",
    19: "When scale changes what can be heard, length stops being an expense and becomes a source of form.",
    20: "That uncertain neighborhood can sustain return without reducing it to confirmation.",
    21: "A process can remain almost hidden and still leave the listener with unmistakable evidence of motion.",
    22: "Length then becomes available as a real choice, reserved for relations that need time to become themselves.",
    23: "When local gestures can stand on their own, anticipation gains room to breathe.",
    24: "The useful response is curiosity: what has stopped changing, and what small decision could make time active again?",
    25: "Treating those lived hours as material can make duration more humane and more exact at once.",
    26: "Necessity does not make the work austere; it gives every minute a reason to belong.",
    27: "That threshold is a practical discovery: it tells you how long uncertainty needs in order to live.",
    28: "A well-shaped span gives the next limit real force: whatever enters now has time enough to matter.",
    29: "A strong boundary does not close the work; it concentrates the place where invention can begin.",
    30: "Meeting a condition actively can turn an inherited limit into audible character without pretending the condition was a gift.",
    31: "Finish the sentence clearly, and the constraint becomes a promise the music can test.",
    32: "Prepare the field carefully, and even a modest exception can change the scale of the whole.",
    33: "That is the freedom a useful rule creates: not fewer decisions, but decisions whose consequences can be heard.",
    34: "The report is valuable: it tells the composer where the method must become music.",
    35: "A clear hierarchy lets the rules generate motion instead of merely policing it.",
    36: "Consequences are where a borrowed limit becomes a composer's own field of discovery.",
    37: "Once simplicity loses its halo, its actual expressive range becomes much larger.",
    38: "A rule that can answer pressure rather than merely survive it has begun to behave like form.",
    39: "Inside such a boundary, resistance is not failure; it is the music showing you where to continue.",
    40: "When the difficulty is audible, performers and listeners can meet it as part of the work rather than as a hidden cost.",
    41: "That is where the boundary pays off: one sound can now become large enough to investigate.",
    42: "That is the promise of sustain: continuity can enlarge a sound until its smallest motions begin to carry form.",
    43: "Once the means of continuation is chosen deliberately, the line becomes a field of audible decisions.",
    44: "Listen at those stages, and one written note opens into several compositional times.",
    45: "Treat that motion as material, and a single interval can generate pulse, density, and arrival without adding an attack.",
    46: "Once one note is allowed an interior, limitation becomes depth rather than deprivation.",
    47: "Heard as a function, the drone becomes flexible again: it can ground one relation, expose another, and change jobs over time.",
    48: "Every resonant body therefore offers a different continuation, and choosing among them is already a way of shaping form.",
    49: "When that care becomes audible, duration can reveal collaboration rather than conceal effort.",
    50: "Wait for that final part, and release can supply the transition you might otherwise have written as a new event.",
    51: "Hearing the cost does not diminish continuity; it gives the sustained sound a body, a history, and stakes.",
    52: "Choose that motion clearly, and one sound can travel without abandoning its name.",
    53: "Composing the handoff lets continuity feel larger than any single source that produces it.",
    54: "A stable reference does not close the harmonic world; it gives every arriving pitch a newly audible distance.",
    55: "The reward is a harmony that can remain open without becoming vague, and stable without becoming inert.",
    56: "Define the behavior, and even a small collection can begin to offer paths, thresholds, and return.",
    57: "Once those forces are audible, the composer can strengthen, contradict, or gradually transfer their weight.",
    58: "That recognition expands the field: inherited categories become choices rather than laws.",
    59: "Move the floor deliberately, and fixed pitches can travel farther than a progression.",
    60: "That exposure is useful: a single moving voice can make an apparently static chord undertake a real journey.",
    61: "This leaves a wide field between cadence and weightlessness, ready to be composed rather than merely labeled.",
    62: "Compose the distances, and the chord can change posture before it changes pitch.",
    63: "Once behavior enters the design, tuning becomes a source of phrase and form rather than a preliminary calculation.",
    64: "Sustain both hearings clearly, and uncertainty becomes a field the listener can explore rather than a problem awaiting correction.",
    65: "Give the field that uneven terrain, and return, departure, and surprise become possible without importing a conventional progression.",
    66: "When those consequences remain audible, the harmonic method can support more than one character without losing its identity.",
    67: "A charged ambiguity gives the next gesture somewhere meaningful to lean, whichever center it favors.",
    68: "Shared climate need not produce unanimity; it can give independent lines the confidence to separate.",
    69: "Once the invariant is clear, every other parameter becomes newly available for invention.",
    70: "That transformation is a gift of recurrence: familiar material can keep acquiring new functions without being replaced.",
    71: "Hold the reference steady, and changes too small to stand alone can begin to write the larger form.",
    72: "Cross those levels deliberately, and a modest cell can cast consequences far beyond its own length.",
    73: "Designing for those human changes lets a repeated score become a living duration rather than a copy machine.",
    74: "A well-made cycle can hold collective freedom without dissolving the common world.",
    75: "What leaves can shape the form as strongly as what enters, because the listener keeps carrying the missing layer forward.",
    76: "Protecting the invariant gives transformation room to become unmistakable.",
    77: "Careful repetition does not freeze its object; it creates the conditions in which that object's irregular life can be heard.",
    78: "When the ground is strong enough, travel can become daring without becoming arbitrary.",
    79: "Compose with the ending already latent in the cycle, and every return can lean toward a different fate.",
    80: "That is encouraging news: the same method can support radically different music when its conditions are chosen precisely.",
    81: "The result can belong to the players in front of you while retaining a structure strong enough to be shared again.",
    82: "Let the returning phrase keep its identity, and separation itself becomes material.",
    83: "Once those relations are composed, independence can produce clarity, surprise, and common form at once.",
    84: "A clear agreement gives separation meaning and gives the eventual return somewhere to land.",
    85: "Answer them, and an apparently free texture gains a temporal profile the ear can follow.",
    86: "Choose that degree carefully, and phase becomes a moving perspective rather than a demonstration of a trick.",
    87: "With that room, performers can turn a tiny pattern into a precise instrument for hearing relationship.",
    88: "The right independence does not make the music vague; it makes one question more audible.",
    89: "Prepare that recognition, and a fleeting crossing can carry the force of an arrival.",
    90: "Used where it matters, bodily measure can give a phrase both flexibility and an unmistakable human scale.",
    91: "Give one meeting a consequence, and coincidence can open a new region of the piece.",
    92: "A clear boundary does not diminish freedom; it gives performers enough common ground to use it boldly.",
    93: "Restore that relation, and even a blurred passage can regain direction without losing its looseness.",
    94: "The plan gives drift a beginning; listening gives it discoveries worth keeping.",
    95: "Preserve the function rather than the furniture, and the pulse can keep the ensemble related while its surface stays alive.",
    96: "That transformation opens a new compositional scale: not only when parts meet, but what their meeting allows us to hear.",
    97: "Once jobs can change, a handful of strands can generate a form much larger than their inventory.",
    98: "Composing legibility this way lets familiar material keep changing its social life inside the texture.",
    99: "That gives the composer motion without replacement: the same things can keep becoming a different whole.",
    100: "Change the consequence, and density becomes a verb rather than a head count.",
    101: "Draw those relations deliberately, and register can make a texture approach, withdraw, open, or close without adding a line.",
    102: "A composed threshold lets the ear enjoy both scales: the life of one line and the force of the many.",
    103: "What survives the clearing has earned a chance to carry the next part of the form.",
    104: "When those relations are tuned carefully, apparent stillness can keep producing fresh internal events.",
    105: "Shape what each arrival changes, and accumulation becomes a journey rather than a receipt.",
    106: "Letting one unnecessary layer go may return consequence to every layer that remains.",
    107: "That difference is not a defect to eliminate; it may be the opening through which the live form enters.",
    108: "Once the relation is audible, even one remaining strand may contain enough difference to continue the form.",
    109: "Compose those dimensions directly, and a single note can arrive with the formal force of a new harmony.",
    110: "That range gives every familiar instrument more compositional futures than its name suggests.",
    111: "Once color has verbs, it can carry continuity, contrast, and return with the precision usually reserved for pitch.",
    112: "A discovered difference becomes useful when you can bring it back, alter its role, and make its return matter.",
    113: "Shape that trajectory, and the sound itself can supply the phrase the notation only begins.",
    114: "Find that permission, and the combined sound becomes a third participant rather than a compromise.",
    115: "Working accurately with what sound carries can deepen transformation rather than restrict it.",
    116: "Compose the remainder, and one release can become the threshold of the next event.",
    117: "Restore a real difference, and color regains the power to alter what can happen next.",
    118: "Once the convenient signal is removed, the surviving structure reveals what the colors themselves can do.",
    119: "When those choices become audible, releasing control can enlarge the work without making responsibility disappear.",
    120: "When that next agent is chosen clearly, the work can become more responsive without becoming less composed.",
    121: "Mapping decisions this way reveals new places for trust, structure, and surprise.",
    122: "When responsibility is legible, performers can act decisively instead of guessing what freedom was supposed to mean.",
    123: "A clear identity gives the surface room to surprise everyone, including the composer.",
    124: "Responsibility is not the enemy of chance; it is what lets chance become a serious compositional partner.",
    126: "Compose that attentiveness well, and relationships can produce detail no individual part could contain.",
    127: "Named capacity turns openness from abdication into collaboration.",
    128: "Following that chain can enlarge authorship without allowing anyone's contribution to vanish.",
    129: "When risk and recognition are visible, performers can offer more of their judgment without being asked to disappear into the result.",
    130: "Once those distributions are audible, they can be revised, and the ensemble can discover forms of leadership the composer could not assign in advance.",
    131: "Designing a way back gives performers permission to take risks that a brittle form would punish.",
    132: "Clear ownership makes freedom usable: each open decision can carry actual consequence instead of decorative uncertainty.",
    133: "The family succeeds when its members remain recognizably related and genuinely capable of surprising one another.",
    134: "Each revision can move freedom closer to the knowledge that makes it musically alive.",
    135: "As responsibility widens beyond the ensemble, the surrounding world becomes capable of changing the piece in turn.",
    136: "Writing those conditions into the work can make place an active collaborator without pretending it is a neutral instrument.",
    137: "Once a local event can alter a decision, every performance gains a way to discover where it actually is.",
    138: "Leave the room that work, and architecture can become a temporal voice rather than an added effect.",
    139: "That precision makes portability and specificity available as choices, not opposing virtues.",
    140: "Accurate naming can deepen a work's relation to place because it replaces borrowed atmosphere with actual history.",
    141: "Compose those differences, and movement can reveal a piece no fixed seat could contain.",
    142: "A function can give music more ways to matter, not fewer.",
    143: "Answering that question turns atmosphere from a finish applied to the music into a relation the music can change.",
    144: "A site-shaped origin can remain generative elsewhere, carrying questions that each new room must answer differently.",
    145: "When the world refuses the premise, the piece has an opportunity to become more situated rather than less itself.",
    146: "Care at that scale can make public music more adventurous, because its pressure no longer depends on unchosen captivity.",
    147: "Consequence gives atmosphere direction: the music can support, expose, interrupt, or make room.",
    148: "Composing that return lets the ending give the place back changed in attention, if not in fact.",
    149: "That outside hearing may reveal a formal condition no rehearsal inside the ensemble could detect.",
    150: "The room's return offers one clue: an ending can release a world whose continuation the piece has taught us to hear.",
    151: "That definition gives every continuation a task and every ending something precise to answer.",
    152: "Choose the verbs clearly, and even a spare diagram can begin to generate dramatic consequence.",
    153: "When the reason changes, continuation stops being mere extension and becomes discovery.",
    154: "A strong opening creates possibility by making later difference consequential.",
    155: "Find that place, and a small alteration can move the whole form farther than a page of new material.",
    156: "Once the clocks can be distinguished, their rare agreements can carry enormous weight.",
    157: "A modest answer is enough to renew a state and give continuation fresh purpose.",
    158: "That capacity for contradiction lets a procedure discover an ending rather than merely arrive at one.",
    159: "Selecting the necessary threshold can give a short form completeness and a long form room to breathe.",
    160: "Finding that scale lets aftersound continue the form without asking it to impersonate eternity.",
    161: "Name the verb, and the ending becomes a consequence rather than a stop sign.",
    162: "Within that limit lies a generous possibility: the work can shape its departure without occupying everything that follows.",
    163: "That backward change is the ending's creative power: it lets the final decision reorganize everything already heard.",
    164: "The interval may contain the most honest ending available: the moment control loosens and listening continues.",
    165: "A relation worth continuing is not an unfinished ending. It is the space in which another decision can become necessary.",
}


def insert_for(path: Path) -> int:
    blocks = re.split(r"\n{2,}", path.read_text(encoding="utf-8").strip())
    output: list[str] = []
    current_number: int | None = None
    inserted = 0
    reformatted = 0
    known_sentences = set(LIFT_SENTENCES.values())

    def flattened(text: str) -> str:
        return re.sub(r"\s+", " ", text.strip())

    def wrapped(text: str) -> str:
        return textwrap.fill(
            text,
            width=79,
            break_long_words=False,
            break_on_hyphens=False,
        )

    def append_lift() -> None:
        nonlocal inserted
        if current_number not in LIFT_SENTENCES:
            return
        sentence = LIFT_SENTENCES[current_number]
        if not any(sentence in flattened(block) for block in output):
            output.append(wrapped(sentence))
            inserted += 1

    for block in blocks:
        if (
            flattened(block) in known_sentences
            and block != wrapped(flattened(block))
        ):
            block = wrapped(flattened(block))
            reformatted += 1
        heading = NUMBERED_HEADING.match(block)
        if heading:
            append_lift()
            current_number = int(heading.group(1))
        elif current_number is not None and block in {"---", "## Notes"}:
            append_lift()
            current_number = None
        output.append(block.rstrip())

    append_lift()
    if inserted or reformatted:
        path.write_text("\n\n".join(output).rstrip() + "\n", encoding="utf-8")
    return inserted


def main() -> None:
    total = 0
    for path in sorted(CHAPTER_DIR.glob("[0-9][0-9]-*.md")):
        count = insert_for(path)
        if count:
            print(f"{path.name}: inserted {count}")
            total += count
    print(f"Inserted {total} lift sentences.")


if __name__ == "__main__":
    main()

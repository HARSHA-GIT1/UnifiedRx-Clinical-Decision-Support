"""
Seed script: populates drug_interaction_knowledge_base with 12 curated
interaction pairs (8 Allopathy-AYUSH cross-system, 4 Allopathy-Allopathy).

All names stored in lowercase generic form to match the lookup key used by
the safety engine (_lookup_name -> generic_name.lower()).

References:
  - WHO Global Report on Traditional and Complementary Medicine 2019
  - Indian Pharmacopoeia (IP 2022)
  - Drugs.com interaction database
  - Borrelli & Izzo (2009), Herb-Drug Interactions methodology
"""

import asyncio
from sqlalchemy import select
from app.core.database import async_session_factory
from app.models.drug_interaction import DrugInteraction

INTERACTION_PAIRS = [
    {
        "medicine_a": "warfarin",
        "medicine_b": "withania somnifera",
        "severity": "Major",
        "evidence": (
            "Ashwagandha (Withania somnifera) may enhance the anticoagulant effect of "
            "warfarin, increasing bleeding risk. Mechanism: possible CYP2C9 inhibition "
            "and additive anticoagulant activity."
        ),
        "clinical_reference": "IP 2022; Ulbricht et al. Natural Standard Herb & Supplement Guide",
    },
    {
        "medicine_a": "warfarin",
        "medicine_b": "curcumin",
        "severity": "Major",
        "evidence": (
            "Curcumin inhibits platelet aggregation and potentiates warfarin anticoagulation "
            "via CYP2C9 inhibition. Co-administration significantly raises INR."
        ),
        "clinical_reference": "Drugs.com; Jiang et al. Drug Metab Pharmacokinet 2012",
    },
    {
        "medicine_a": "amoxicillin and clavulanate potassium",
        "medicine_b": "commiphora mukul",
        "severity": "Moderate",
        "evidence": (
            "Guggul (Commiphora mukul) may reduce bioavailability of certain antibiotics "
            "via P-glycoprotein induction, potentially decreasing efficacy of co-administered "
            "amoxicillin-clavulanate."
        ),
        "clinical_reference": "WHO TCM Report 2019; Williamson et al. Major Herbs of Ayurveda",
    },
    {
        "medicine_a": "metformin hydrochloride",
        "medicine_b": "momordica charantia",
        "severity": "Moderate",
        "evidence": (
            "Bitter melon (Karela / Momordica charantia) has independent hypoglycaemic "
            "activity. Concurrent use with metformin may cause additive hypoglycaemia "
            "requiring dose monitoring."
        ),
        "clinical_reference": "Fuangchan et al. J Ethnopharmacol 2011; IP 2022",
    },
    {
        "medicine_a": "aspirin",
        "medicine_b": "zingiber officinale",
        "severity": "Moderate",
        "evidence": (
            "Ginger (Zingiber officinale) inhibits thromboxane synthase and has additive "
            "antiplatelet effect with aspirin, increasing bleeding risk."
        ),
        "clinical_reference": "Drugs.com; Srivastava KC. Prostag Leukot Med 1986",
    },
    {
        "medicine_a": "digoxin",
        "medicine_b": "glycyrrhiza glabra",
        "severity": "Major",
        "evidence": (
            "Liquorice (Glycyrrhiza glabra) causes pseudohyperaldosteronism leading to "
            "hypokalaemia, which potentiates digoxin toxicity and risk of arrhythmia."
        ),
        "clinical_reference": "IP 2022; Bernardi et al. Lancet 1994",
    },
    {
        "medicine_a": "methotrexate",
        "medicine_b": "curcumin",
        "severity": "Moderate",
        "evidence": (
            "Curcumin may inhibit OATP1B1 hepatic transporter, reducing methotrexate "
            "clearance and increasing plasma levels and toxicity risk."
        ),
        "clinical_reference": "Drugs.com; van de Steeg et al. Drug Metab Dispos 2012",
    },
    {
        "medicine_a": "phenytoin",
        "medicine_b": "convolvulus pluricaulis",
        "severity": "Major",
        "evidence": (
            "Shankhapushpi (Convolvulus pluricaulis) significantly reduces phenytoin blood "
            "levels, risking loss of seizure control. Mechanism not fully elucidated; "
            "likely accelerated metabolism or reduced absorption."
        ),
        "clinical_reference": "Dandekar et al. J Ethnopharmacol 1992; IP 2022",
    },
    {
        "medicine_a": "amoxicillin and clavulanate potassium",
        "medicine_b": "metronidazole",
        "severity": "Moderate",
        "evidence": (
            "Combined aminopenicillin and metronidazole therapy carries additive "
            "hepatotoxic risk, particularly with prolonged courses. Monitor LFTs."
        ),
        "clinical_reference": "Drugs.com; BNF 2023",
    },
    {
        "medicine_a": "aspirin",
        "medicine_b": "ibuprofen",
        "severity": "Moderate",
        "evidence": (
            "Ibuprofen may competitively and reversibly inhibit aspirin-binding to "
            "COX-1, reducing aspirin antiplatelet effect when taken concurrently. "
            "Cardioprotective benefit of low-dose aspirin may be reduced."
        ),
        "clinical_reference": "FDA Drug Safety Communication 2006; MacDonald TM et al. Lancet 2003",
    },
    {
        "medicine_a": "simvastatin",
        "medicine_b": "amoxicillin and clavulanate potassium",
        "severity": "Minor",
        "evidence": (
            "Minor CYP3A4 pharmacokinetic interaction. Amoxicillin-clavulanate may "
            "slightly alter simvastatin metabolism. Clinical significance is low."
        ),
        "clinical_reference": "Drugs.com",
    },
    {
        "medicine_a": "metformin hydrochloride",
        "medicine_b": "metronidazole",
        "severity": "Minor",
        "evidence": (
            "Metronidazole may slightly increase metformin plasma levels via competitive "
            "inhibition of renal OCT2 transporter. Monitor blood glucose with prolonged "
            "co-administration."
        ),
        "clinical_reference": "Drugs.com; Somogyi et al. Br J Clin Pharmacol 1987",
    },
]


async def seed_interaction_data():
    async with async_session_factory() as db:
        added = 0
        for pair in INTERACTION_PAIRS:
            stmt = select(DrugInteraction).where(
                (
                    (DrugInteraction.medicine_a == pair["medicine_a"])
                    & (DrugInteraction.medicine_b == pair["medicine_b"])
                ) | (
                    (DrugInteraction.medicine_a == pair["medicine_b"])
                    & (DrugInteraction.medicine_b == pair["medicine_a"])
                )
            )
            existing = (await db.execute(stmt)).scalar_one_or_none()
            if not existing:
                db.add(DrugInteraction(
                    medicine_a=pair["medicine_a"],
                    medicine_b=pair["medicine_b"],
                    severity=pair["severity"],
                    evidence=pair["evidence"],
                    clinical_reference=pair["clinical_reference"],
                ))
                added += 1
        await db.commit()
        print(f"Seeded {added} drug interaction pairs ({len(INTERACTION_PAIRS) - added} already existed).")


if __name__ == "__main__":
    asyncio.run(seed_interaction_data())

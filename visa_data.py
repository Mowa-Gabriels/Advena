

VISA_DESCRIPTIONS: dict[str, str] = {
    "H-1B": "For professionals in 'specialty occupations' requiring a bachelor's degree or higher. Needs a specific job offer from a U.S. employer.",
    "L-1": "For employees of an international company being transferred to a U.S. office as a manager, executive, or specialist.",
    "O-1": "For individuals with extraordinary ability or achievement in sciences, arts, education, business, or athletics.",
    "TN": "For eligible citizens of Canada and Mexico working in specific professional occupations under USMCA.",
    "H-2A/H-2B": "For temporary or seasonal workers in agricultural (H-2A) or non-agricultural (H-2B) fields with U.S. worker shortages.",
    "P Visas": "For internationally recognized athletes, artists, and entertainers performing in the U.S.",
    "R-1": "For religious workers coming to work for a non-profit religious organization in the U.S.",
    "EB-1": "Green Card for individuals of extraordinary ability, outstanding professors/researchers, or multinational executives.",
    "EB-2": "Green Card for professionals with advanced degrees or individuals with exceptional ability.",
    "EB-3": "Green Card for skilled workers, professionals with bachelor's degrees, and other workers.",
    "EB-5": "Green Card for foreign investors making a significant capital investment that creates U.S. jobs.",
    "F-1": "For full-time academic students enrolled in an accredited U.S. college, university, or academic institution.",
    "J-1": "For participants in work-and-study-based exchange visitor programs.",
    "M-1": "For students pursuing vocational or non-academic courses at a recognized U.S. institution.",
    "K-1": "For the fiancé(e) of a U.S. citizen to travel to the U.S. with intent to marry within 90 days.",
    "K-3": "For the spouse of a U.S. citizen while their immigrant visa application is pending.",
    "IR Visas": "Green Card for 'Immediate Relatives' of a U.S. citizen: spouses, unmarried children under 21, and parents.",
    "F Visas": "Green Card for other family members of U.S. citizens or Lawful Permanent Residents subject to annual quotas.",
    "B-1": "For temporary business visits: conferences, negotiations, consultations. No employment permitted.",
    "B-2": "For temporary tourism, vacation, visiting family/friends, or medical treatment.",
    "C": "For individuals transiting through the U.S. to another country.",
    "I": "For representatives of foreign media: journalists, reporters, and film crews.",
    "D": "For crewmembers working on sea vessels or international aircraft.",
}

GOAL_TO_VISA_MAPPING: dict[str, list[str]] = {
    "Select a Goal...": [],
    "Work in the U.S.": ["H-1B", "L-1", "O-1", "TN", "H-2A/H-2B", "P Visas", "R-1", "EB-1", "EB-2", "EB-3"],
    "Study or Conduct Research": ["F-1", "J-1", "M-1"],
    "Join Family in the U.S.": ["K-1", "K-3", "IR Visas", "F Visas"],
    "Invest in a U.S. Business": ["EB-5"],
    "Visit for a Short Period": ["B-1", "B-2"],
    "Transit or Specialized Travel": ["C", "I", "D"],
}

ASSESSMENT_QUESTIONS: dict[str, list[str]] = {
    "H-1B": [
        "Describe your job offer and why it qualifies as a 'specialty occupation' requiring a bachelor's degree.",
        "How does your education and experience directly match the job's requirements?",
        "Can the sponsoring employer demonstrate ability to pay the prevailing wage for the position?",
    ],
    "L-1": [
        "Describe your continuous employment with the foreign company for at least one year within the last three years.",
        "What is the qualifying relationship between your foreign employer and the U.S. company?",
        "Explain the managerial, executive, or specialized knowledge role you will hold in the U.S.",
    ],
    "O-1": [
        "Provide evidence of sustained national or international acclaim (awards, publications, critical roles).",
        "Describe the specific work activities you intend to undertake in the U.S.",
        "Do you have advisory opinions or expert letters attesting to your extraordinary ability?",
    ],
    "TN": [
        "Are you a citizen of Canada or Mexico?",
        "Do you have a job offer in a USMCA-listed professional occupation?",
        "Do you possess the necessary credentials (degree, license) for that profession?",
    ],
    "H-2A/H-2B": [
        "Does your prospective U.S. employer have a temporary or seasonal need for workers?",
        "Is the work agricultural (H-2A) or non-agricultural (H-2B)?",
        "Can the employer demonstrate insufficient U.S. workers for the temporary work?",
    ],
    "P Visas": [
        "Can you demonstrate you are an internationally recognized athlete, artist, or entertainer?",
        "Will your performance require a performer of your caliber?",
        "Provide evidence of international recognition (awards, media, critical reviews).",
    ],
    "R-1": [
        "Are you seeking to work in a religious vocation or occupation?",
        "Is the U.S. organization a bona fide non-profit religious organization?",
        "Have you been a member of the religious denomination for at least two years?",
    ],
    "EB-1": [
        "Describe your evidence of extraordinary ability (major awards, publications, high salary, critical roles).",
        "For outstanding professors/researchers: provide evidence of at least 3 years' experience and international recognition.",
        "For multinational executives: detail your managerial/executive employment abroad and the U.S. role.",
    ],
    "EB-2": [
        "Do you hold an advanced degree (Master's or higher) or demonstrate exceptional ability?",
        "If claiming exceptional ability, provide evidence meeting at least three of the specified criteria.",
        "How does your proposed U.S. work substantially benefit the national interest (if seeking an NIW)?",
    ],
    "EB-3": [
        "Do you have a job offer for a skilled worker position (requiring 2+ years training) or a professional role?",
        "Do you meet the educational and experience requirements for the specific job?",
        "Has your prospective employer completed the PERM labor certification process?",
    ],
    "F-1": [
        "Provide details of the U.S. school, program, and your Form I-20.",
        "How will you cover tuition and living expenses without unauthorized employment?",
        "Describe your ties to your home country and plans after completing your studies.",
    ],
    "J-1": [
        "What is the specific exchange visitor program category (student, researcher, intern, au pair)?",
        "Can you demonstrate sufficient English proficiency to participate?",
        "Do you meet the educational or professional requirements of the program?",
    ],
    "M-1": [
        "Provide details of the U.S. vocational institution, program, and your Form I-20.",
        "How will you cover tuition and living expenses during your training?",
        "Describe your ties to your home country and plans after your vocational studies.",
    ],
    "K-1": [
        "Are you the fiancé(e) of a U.S. citizen?",
        "Can you prove you met your U.S. citizen fiancé(e) in person within the last two years?",
        "Do you intend to marry within 90 days of arrival in the U.S.?",
    ],
    "K-3": [
        "Are you the spouse of a U.S. citizen?",
        "Is an I-130 petition filed by your U.S. citizen spouse still pending?",
        "Can you demonstrate that your marriage is bona fide?",
    ],
    "IR Visas": [
        "Are you the spouse, unmarried child (under 21), or parent of a U.S. citizen?",
        "Can you provide proof of the qualifying family relationship?",
        "Is your U.S. citizen family member willing and able to financially sponsor you?",
    ],
    "F Visas": [
        "What is your relationship to the U.S. citizen or LPR sponsoring you?",
        "Can you provide proof of the qualifying family relationship?",
        "Is your sponsoring family member willing and able to financially sponsor you?",
    ],
    "EB-5": [
        "Are you prepared to invest $1,050,000 (or $800,000 in a TEA) in a U.S. commercial enterprise?",
        "Can you demonstrate that your investment will create at least 10 full-time jobs for qualifying U.S. workers?",
        "Can you prove the lawful source of your investment funds?",
    ],
    "B-1": [
        "What is the specific purpose of your business visit (conferences, negotiations, consultations)?",
        "Can you confirm you will not engage in employment in the U.S.?",
        "Do you have a clear intent to depart and strong ties to your home country?",
    ],
    "B-2": [
        "What is the specific purpose of your visit (vacation, family, medical treatment)?",
        "Can you demonstrate sufficient funds to cover your expenses?",
        "Do you have a clear intent to depart and strong ties to your home country?",
    ],
    "C": [
        "Are you transiting directly through the U.S. en route to another country?",
        "Do you have a confirmed onward ticket to your final destination?",
        "Can you demonstrate your sole purpose in the U.S. is transit?",
    ],
    "I": [
        "Are you a representative of foreign media (journalist, reporter, film crew)?",
        "Is your primary purpose engaging in your media profession for a foreign outlet?",
        "Can you demonstrate a bona fide affiliation with a foreign media organization?",
    ],
    "D": [
        "Are you a crewmember working on a sea vessel or international aircraft?",
        "Is your name on the manifest of the vessel or aircraft?",
        "Can you demonstrate that your U.S. entry is solely to perform crewmember duties?",
    ],
}

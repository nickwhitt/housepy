from housepy.models.event import Event
from housepy.models.family import Family
from housepy.models.house import House
from housepy.models.name import Name
from housepy.models.person import Person
from housepy.models.title import Tenure, Title

titles = [
    Title("hesse-darmstadt.landgrave", "Landgrave of Hesse-Darmstadt"),
    Title("hesse-and-by-rhine.grand-duke", "Grand Duke of Hesse and by Rhine"),
]

houses = [
    House("hesse", "Hesse"),
    House(
        "hesse-darmstadt",
        "Hesse-Darmstadt",
        parent="hesse",
        founder="hesse-darmstadt.ludwig-ix",
        founded=Event(1740),
    ),
]

people = [
    Person(
        "hesse-darmstadt.ludwig-ix",
        Name(chosen="Ludwig IX", given="Ludwig"),
        Event(1719, 12, 15, "Darmstadt, Landgraviate of Hesse-Darmstadt"),
        Event(1790, 4, 6),
        [Tenure.regnal("hesse-darmstadt.landgrave", Event(1768, 10, 12))],
        house="hesse-darmstadt",
    ),
    Person(
        "hesse-darmstadt.friederike-luise",
        Name("Friederike Luise", "Hesse-Darmstadt", "of"),
        Event(1751, 10, 16, "Prenzlau, Electorate of Brandenburg"),
        Event(1805, 2, 25),
        house="hesse-darmstadt",
    ),
    Person(
        "hesse-darmstadt.ludwig-i",
        Name(chosen="Ludwig I", given="Ludwig"),
        Event(1753, 6, 14, "Prenzlau, Margraviate of Brandenburg"),
        Event(1830, 4, 6),
        [
            Tenure.regnal("hesse-and-by-rhine.grand-duke", Event(1806, 8, 14)),
            Tenure.regnal(
                "hesse-darmstadt.landgrave",
                Event(1790, 4, 6, name=Name(chosen="Ludwig X")),
                demise=Event(1806, 8, 14),
            ),
        ],
        house="hesse-darmstadt",
    ),
]

families = [
    Family(
        "hesse-darmstadt.ludwig-ix+hesse-darmstadt.friederike-luise+family-1",
        "hesse-darmstadt.ludwig-ix",
        "hesse-darmstadt.friederike-luise",
        ["hesse-darmstadt.ludwig-i"],
        Event(1741, 8, 12, "Zweibrücken, Duchy of Palatinate-Zweibrücken"),
    )
]

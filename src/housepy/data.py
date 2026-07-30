from housepy.models.event import Event
from housepy.models.name import Name
from housepy.models.person import Person
from housepy.models.title import Tenure, Title

titles = [
    Title("hesse-darmstadt.landgrave", "Landgrave of Hesse-Darmstadt"),
    Title("hesse-and-by-rhine.grand-duke", "Grand Duke of Hesse and by Rhine"),
]

people = [
    Person(
        "hesse-darmstadt.ludwig-ix",
        Name.regnal("Ludwig IX", "Hesse-Darmstadt", "Ludwig"),
        Event(1719, 12, 15, "Darmstadt, Landgraviate of Hesse-Darmstadt"),
        Event(1790, 4, 6),
        [Tenure.regnal("hesse-darmstadt.landgrave", Event(1768, 10, 12))],
    ),
    Person(
        "hesse-darmstadt.friederike-luise",
        Name("Friederike Luise", "Hesse-Darmstadt", "of", format=Name.FULL),
        Event(1751, 10, 16, "Prenzlau, Electorate of Brandenburg"),
        Event(1805, 2, 25),
    ),
    Person(
        "hesse-darmstadt.ludwig-i",
        Name.regnal("Ludwig I", "Hesse-Darmstadt", "Ludwig"),
        Event(1753, 6, 14, "Prenzlau, Margraviate of Brandenburg"),
        Event(1830, 4, 6),
        [
            Tenure.regnal("hesse-and-by-rhine.grand-duke", Event(1806, 8, 14)),
            Tenure.regnal(
                "hesse-darmstadt.landgrave",
                Event(1790, 4, 6, name=Name.regnal("Ludwig X")),
                demise=Event(1806, 8, 14),
            ),
        ],
    ),
]

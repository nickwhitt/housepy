from typing import Literal

# A unique identifier string (Person/Title/Family slug). Uniqueness is a
# convention, not something enforced at the type level.
type Slug = str

# male or female; None means not recorded, not a third value.
type Sex = Literal["male", "female"]

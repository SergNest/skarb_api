from typing import Optional

from pydantic import BaseModel


class SMassage(BaseModel):
    lo_address: str
    chat_id: Optional[int] = -4076579827
    movement: Optional[str] = 'buy'
    val: Optional[str] = 'USD'
    val_sum: int = 50
    val_national_sum: float = 2007.5
    course: float = 40.15
<<<<<<< HEAD

=======
>>>>>>> 5642356f315e381a164b884ef6b79a8959b12480
    # for another notification
    usd_rate: Optional[str] = None
    eur_rate: Optional[str] = None

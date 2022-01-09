from pydantic import BaseModel, validator, root_validator

class SqlPrepare(BaseModel):
    sql: str
    data: tuple

class ElaMetric(BaseModel):
    dt: str
    mac_addr: str
    rssi: int
    cn: str
    category: str
    value: float

    def sql_insert(self, tbl):
        sql = f'INSERT INTO {tbl} (dt, mac_addr, rssi, cn, category, value) VALUES (?,?,?,?,?,?);'
        return SqlPrepare(sql=sql, data=(self.dt, self.mac_addr, self.rssi, self.cn, self.category, self.value))

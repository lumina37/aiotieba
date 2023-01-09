import pytest

import aiotieba as tb


@pytest.mark.asyncio
async def test_Database(db: tb.MySQLDB):
    fname = db.fname
    fid = await db.get_fid(fname)
    assert fname == await db.get_fname(fid)
    await db.get_userinfo("v_guard")
    await db.get_tid(7763274602)
    await db.get_user_id_list()
    await db.get_tid_list(limit=3)

from lib.sost_logging import dong_log
log = dong_log()
log.debug_flags = str(log.json_get("debug","debug_flags",filename="debug"))
print(str(log.json_get("debug","debug_flags",filename="debug")))

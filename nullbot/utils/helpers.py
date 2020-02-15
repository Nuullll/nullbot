from nullbot.config import MAX_MESSAGE_LEN

def multiline_msg_generator(lines=None, lineno=False, lineno_format='#{} ', max_msg_len=MAX_MESSAGE_LEN):
    msg = ''
    sz = 0
    for i, line in enumerate(lines):
        if lineno:
            msg += lineno_format.format(i)

        msg += line + '\n'
        sz += len(line)

        if sz > max_msg_len:
            yield msg.strip()
            msg = ''
            sz = 0
    
    yield msg.strip()

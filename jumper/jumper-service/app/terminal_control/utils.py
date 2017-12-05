# -*- coding: utf-8 -*-

from app.lib.utils import get_colour


def get_commands():
    """ tab提示所有命令 """
    cc = [
        'h',
        'H',
        'help',
        'i',
        'info',
        'information',
        'r',
        'R',
        'p',
        'password',
        'u',
        'U',
        'user',
        'id',
        'ssh',
        'ping',
        'history',
        'q',
        'exit',
        'pssh',
        'plog',
        'getapp',
        'gethost',
        'play',
        'config'
    ]
    return cc


def tab_history(cmd, cmd_history):
    cmd_prefix = cmd.split()[0]
    search_string = cmd.split(cmd_prefix)[1:][0].lstrip()
    history = set()
    for x in cmd_history:
        if x.startswith(cmd_prefix):
            left_args = x[len(cmd_prefix):].strip()
            if len(left_args) > 0:
                history.add(left_args)
    return search_string, [i for i in history if i.startswith(search_string)]


def tab_command(command_prefix):
    if command_prefix.strip():
        return [x for x in get_commands() if x.startswith(command_prefix)]
    else:
        return get_commands()


def retrieve_command(cmd, history, index=0):
    """
    两种情况
    1, ctrl + r 继续回溯, 此时需要记录pos向前回溯
    2, 命令发生变化, 此时index重新回到0开始回溯
    无论哪种回溯都会对命令进行去重
    """
    _history = list(set(history))
    if not cmd:
        for pos, x in enumerate(_history[index:]):
            return x, pos + index + 1, 0
    for pos, x in enumerate(_history[index:]):
        if cmd in x:
            backspace = len(x) - x.index(cmd)
            return x, pos + index + 1, backspace


# 根据窗口size整齐排列
def terminal_format(commands, terminal, channel):
    # 每行 3 列, 30个字符等宽
    result = ''
    rows = ''
    if terminal.get(channel) and terminal.get(channel).get('width'):
        terminal_width = int(terminal[channel].get('width'))
    else:
        terminal_width = 120
    for col in commands:
        if (terminal_width - len(rows)) < 30:
            result = result.strip() + u'\r\n%-30s\t' % col
            rows = u'%-30s\t' % col
            continue
        result += u'%-30s\t' % col
        rows += u'%-30s\t' % col
    result += u'\r\n'
    return get_colour(result, colour='green')

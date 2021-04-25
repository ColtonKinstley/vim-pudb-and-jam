# vim: tw=79
import vim

from bdb import Breakpoint
from itertools import starmap
from linecache import checkcache
from pudb.settings import load_breakpoints, save_breakpoints
from pudb import NUM_VERSION

LOAD_ARGS = () if NUM_VERSION >= (2013, 1) else (None,)


def breakpoints():
    """
    :return: An iterator over the saved breakpoints.
    :rtype: starmap(Breakpoint)
    """
    return starmap(Breakpoint, load_breakpoints(*LOAD_ARGS))


def breakpoint_dict():
    """
    :return: The saved breakpoints, as a dict with (filename, line number) keys
    :rtype: dict(tuple(str, int), Breakpoint)
    """
    return {(bp.file, bp.line): bp for bp in breakpoints()}


def breakpoint_strings():
    """
    :return: An generator over the saved breakpoints as strings in the format:
        "filename:linenr:condition"
    :rtype: generator(str)
    """
    return (
        '{file}:{line:d}:{cond}'.format(
            file=bp.file,
            line=bp.line,
            cond=bp.cond if bp.cond else ' ')
        for bp in breakpoints()
    )


def update():
    vim.command('call sign_unplace(g:pudb_sign_group)')
    for bp in breakpoints():
        try:
            opts = ('{"lnum": %d, "priority": %d}'
                    % (bp.line, vim.vars['pudb_priority']))

            # Critical to use vim.eval here instead of vim.vars[] to get sign
            # group, since vim.vars[] will render the string as
            # "b'pudb_sign_group'" instead of "pudb_sign_group"
            vim.eval('sign_place(0, "%s", "PudbBreakPoint", "%s", %s)'
                     '' % (vim.eval('g:pudb_sign_group'), bp.file, opts))
        except vim.error:
            # Buffer for the given file isn't loaded.
            continue


def current_position():
    """
    :return: a filename, line number pair, to be used as a key for a
        breakpoint.
    :rtype: tuple(str, int)
    """
    filename = vim.eval('expand("%:p")')
    row, _ = vim.current.window.cursor
    return (filename, row)


def toggle():
    """
    Toggles a breakpoint on the current line.
    """
    bps = breakpoint_dict()
    bp_key = current_position()

    if bp_key in bps:
        bps.pop(bp_key)
    else:
        bps[bp_key] = Breakpoint(*bp_key)

    save_breakpoints(bps.values())
    update()


def edit():
    """
    Edit the condition of a breakpoint on the current line.
    If no such breakpoint exists, creates one.
    """
    bps = breakpoint_dict()
    bp_key = current_position()

    if bp_key not in bps:
        bps[bp_key] = Breakpoint(*bp_key)
    bp = bps[bp_key]

    old_cond = '' if bp.cond is None else bp.cond
    vim.command('echo "Current condition: %s"' % old_cond)
    vim.command('echohl Question')
    vim.eval('inputsave()')
    bp.cond = vim.eval('input("New Condition: ", "%s")' % old_cond)
    vim.eval('inputrestore()')
    vim.command('echohl None')

    save_breakpoints(bps.values())
    update()


def clearAll():
    """
    Clears all pudb breakpoints from all files.
    """
    save_breakpoints([])
    update()


def list_breakpoints():
    """
    Prints a list of all the breakpoints in all files.
    Shows the full file path, line number, and condition of each breakpoint.
    """
    update()
    vim.command('echomsg "Listing all pudb breakpoints:"')
    for bp_string in breakpoint_strings():
        vim.command('echomsg "%s"' % bp_string)


def populateList(list_command):
    """
    Calls the given vim command with a list of the breakpoints as strings in
    quickfix format.
    """
    update()
    qflist = []
    for bp in breakpoints():
        try:
            line = vim.eval('getbufline("%s", %s)'
                            % (bp.file, bp.line))[0]
            if line.strip() == '':
                line = '<blank line>'
        except LookupError:
            line = '<buffer not loaded>'
        qflist.append(':'.join(map(str, [bp.file, bp.line, line])))
    vim.command('%s %s' % (list_command, qflist))


def quickfixList():
    """
    Populate the quickfix list with the breakpoint locations.
    """
    populateList('cgetexpr')


def locationList():
    """
    Populate the location list with the breakpoint locations.
    """
    populateList('lgetexpr')


def clearLineCache():
    """
    Clear the python line cache for the given file if it has changed
    """
    filename = vim.eval('expand("%:p")')
    checkcache(filename)
    update()

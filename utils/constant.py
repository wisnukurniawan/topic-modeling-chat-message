EMOTICON_LIST = (
    ('emoticon_senyum', ['>:]', ':-)', ':)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}', ':^)']),
    ('emoticon_senang', ['>:D', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'XD', 'XD', '=-D', '=D', '=-3', '=3']),
    ('emoticon_sedih', ['>:[', ':-(', ':(', ':-c', ':c', ':-<', ':<', ':-[', ':[', ':{', ':’(']),
    ('emoticon_ejek', ['>:P', ':-P', ':P', 'X-P', 'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-Þ', ':Þ', ':-b', ':b']),
    ('emoticon_kesal', ['>:/', '>:/', ':-/', ':-.', ':/', '=/', ':S']),
    ('emoticon_muka_datar', [':|', ':-|']),
    ('emoticon_kedip', [';)']),
    ('emoticon_shock', ['>:o', '>:O', ':-O', ':O', '°o°', '°O°', ':O', 'o_O', 'o.O', '8-0'])
)

DELIMITER = '_'

NEGATION_WORD = 'tidak'

STOP_WORD = set("""
oke
iya
maaf
terima
kasih
halo
selamat
kak
hai
cakap
nya
""".split())

EXC_STOP_WORD = set("""
tidak
""".split())

'''
Mostly a Python to (Emacs)Lisp pretty printer.

Many AST visitors have been implemented. The useful one
being Elispy, which has a fallback to generic_visit for
cases not handled yet.
'''

import ast
from subprocess import Popen, PIPE

from visitors import Generic, Meta, Elispy
from snippets import snippets


class Source:

    '''
    Packs source related methods into a single unit.
    '''

    def __init__(self, source='None', fn='?'):
        self.source = source
        self.fn = fn

    def load(self, fn):
        with open(fn) as src:
            self.source = ''.join(src.readlines())
        return self

    def of(self, source):
        self.source = source
        return self

    def into(self, visitor):
        self.visitor = visitor
        return self

    def __repr__(self):
        return '<Source [%s]>' % self.source

    def talk(self):
        return list(ast.walk(ast.parse(self.source)))

    def elispy(self):
        '''Parse source then pass the ast to the Elispy visitor.'''
        a = ast.parse(self.source)
        return Elispy().visit(a)

    def debug(self):
        '''Parse source then pass the ast to the Generic visitor.'''
        a = ast.parse(self.source)
        return Generic().visit(a)

    def quotecode(self, code):
        return '```\n%s\n```' % code

    def emacs_eval(self):
        '''
        Submit pretty printed src (from the visitor)
        to `emacs` for evaluation.
        '''

        assert Popen(['which', 'emacs'], stdout=PIPE, stderr=PIPE).stderr \
            is not b''

        wrapper = '(message "%%S" (progn %s))'
        # http://www.emacswiki.org/emacs/BatchMode
        code = self.visitor().visit(ast.parse(self.source))
        emacs = Popen(['emacs', '-batch', '--eval', wrapper % code],
                      stderr=PIPE,
                      stdout=PIPE)
        return emacs.stderr.read().decode('utf8')

    def transpile(self):
        qs = self.quotecode('## %s (Python|source)\n' % self.fn + self.source)
        ast0 = ast.parse(self.source)
        print('[transpile][pre]', ast.dump(ast0))
        ast1 = ast0 if not self.transformer else self.transformer().visit(ast0)
        print('[transpile][post]', ast.dump(ast1))
        tgt = self.visitor().visit(ast1)
        qt = self.quotecode(';; %s (Lisp|target)\n' % self.fn + '\n%s\n' % tgt)
        return qs, qt


def premain(visitor):
    '''Parse test snippets and pass them to visitor.'''
    for name, source in snippets.items():
        qs, qt = Source(source, name.capitalize()).transpile(visitor)
        print(qs)
        print(qt)
        print()


def main():
    '''Helper, calls premain(Elispy).'''
    return premain(Elispy)

# Main

if __name__ == '__main__':

    premain(Elispy)

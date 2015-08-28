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

    def __init__(self, fn, source):
        self.fn = fn
        self.source = source

    def talk(self):
        return list(ast.walk(ast.parse(self.source)))

    def elispy(self):
        ''' parse s then pass it to the Elispy visitor '''
        return Elispy().visit(ast.parse(self.source))

    def debug(self):
        '''Parse source then pass the ast to the Dummy visitor.'''
        a = ast.parse(self.source)
        v = Generic()
        v.visit(a)

    def quotecode(self, code):
        return '''```
%s
```
''' % code

    def emacs_eval(source):
        '''Submit pretty printed src (from the visitor) to `emacs` for evaluation.'''

        assert Popen(['which', 'emacs'], stdout=PIPE, stderr=PIPE).stderr is not b''

        wrapper = '(message "%%S" (progn %s))'
        # http://www.emacswiki.org/emacs/BatchMode
        emacs = Popen(['emacs','-batch','--eval', wrapper % self.source]
                      , stderr=PIPE
                      , stdout=PIPE)
        return emacs.stderr.read().decode('utf8')

    def transpile(self, visitor):
        qs = self.quotecode('## %s (Python|source)\n' % self.fn + self.source)
        tgt = visitor().visit(ast.parse(self.source))
        qt = self.quotecode(';; %s (Lisp|target)\n' % self.fn + '\n' + tgt + '\n')
        return qs, qt

def premain(visitor):
    '''Parse test snippets and pass them to visitor.'''
    for name, source in snippets.items():
        qs, qt = Source(name.capitalize(), source).transpile(visitor)
        print(qs)
        print(qt)
        print()

def main():
    '''Helper, calls premain(Elispy).'''
    return premain(Elispy)

# Main

if __name__ == '__main__':

    premain(Elispy)

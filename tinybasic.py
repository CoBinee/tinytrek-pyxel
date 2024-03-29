# tinybasic.py - Tiny BASIC
#


# 参照
#
import sys
import re
import random
from lark import Lark
from lark import Tree
from lark import Token
from lark import Transformer


# Tiny BASIC クラス
#
class TinyBasic(Transformer):

    # コンストラクタ
    def __init__(self):

        # パスの初期化
        self._path = None

        # リストの初期化
        self._lines = dict()
        self._lists = dict()
        self._nexts = dict()
        self._start = -1

        # ツリーの初期化
        self._trees = dict()

        # 変数の初期化
        self._variables = dict()

        # 配列の初期化
        self._array = dict()

        # GOSUB の初期化
        self._gosubs = list()

        # FOR の初期化
        self._fors = list()

        # デバッグの初期化
        self._debug = False

    # Tiny BASIC を実行する
    def run(self, path):

        # パスの設定
        self._path = path

        # ファイルの読み込み
        if not self._load():
            exit()

        # リストの解析
        if not self._parse():
            exit()

        # プログラムの実行
        if not self._execute():
            exit()

    # ファイルを読み込む
    def _load(self):

        # ファイルの読み込み
        try:
            with open(self._path, 'r', encoding='UTF-8') as file:
                last = -1
                for line in file:
                    match = re.match(r'^\s*(\d+)\s*(.*)\n?$', line)
                    if match is not None:
                        number = int(match.group(1))
                        self._lines[number] = match.group(2)
                        self._nexts[last] = number
                        if self._start < 0 or self._start > number:
                            self._start = number
                        last = number

        # 例外
        except Exception as e:
            sys.stderr.write(f'{e}\n')
            return False

        # 読み込みの完了
        finally:
            pass

        # ステートメント毎に分割
        for number in self._lines.keys():
            line = self._lines[number]
            statement = 0
            head = 0
            length = len(line)
            while head < length:
                while head < length and (line[head] == ' ' or line[head] == '\t'):
                    head = head + 1
                if head < length and re.match(r'^[rR][eE][mM]', line[head:]) is not None:
                    head = length
                else:
                    tail = head
                    while tail < length and line[tail] != ';':
                        if line[tail] == '"':
                            tail = tail + 1
                            while tail < length and line[tail] != '"':
                                tail = tail + 1
                            if tail < length:
                                tail = tail + 1
                        elif line[tail] == "'":
                            tail = tail + 1
                            while tail < length and line[tail] != "'":
                                tail = tail + 1
                            if tail < length:
                                tail = tail + 1
                        else:
                            tail = tail + 1
                    if number not in self._lists:
                        self._lists[number] = dict()
                    self._lists[number][statement] = line[head:tail]
                    statement = statement + 1
                    head = tail + 1

        # 終了
        return True

    # リストを解析する
    def _parse(self):

        # Lark による解析
        try:

            # 文法の定義
            lark = Lark(r'''
                statement           :   command_let
                                    |   command_print
                                    |   command_input
                                    |   command_if
                                    |   command_goto
                                    |   command_gosub
                                    |   command_return
                                    |   command_for
                                    |   command_next
                                    |   command_stop
                command_let         :   ("LET"i)? let ("," let)*
                let                 :   (VARIABLE | array) "=" expression
                command_print       :   ("PRINT"i | "PRIN."i | "PRI."i | "PR."i | "P."i) (STRING | expression | DIGIT)* ("," (STRING | expression | DIGIT))* COMMA?
                command_input       :   ("INPUT"i | "INPU."i | "INP."i | "IN."i) prompt ("," prompt)*
                command_if          :   "IF"i expression statement
                command_goto        :   ("GOTO"i | "GOT."i | "GO."i | "G."i) expression
                command_gosub       :   ("GOSUB"i | "GOSU."i | "GOS."i) expression
                command_return      :   ("RETURN"i | "RETUR."i | "RETU"i | "RET."i | "RE."i | "R."i)
                command_for         :   ("FOR"i | "FO."i | "F."i) VARIABLE "=" expression "TO"i expression (("STEP"i | "STE."i | "ST."i | "S."i) expression)?
                command_next        :   ("NEXT"i | "NEX."i | "NE."i | "N."i) VARIABLE
                command_stop        :   ("STOP"i | "STO."i | "ST."i | "S."i)
                function_abs        :   ("ABS"i | "AB."i | "A."i) "(" expression ")"
                function_rnd        :   ("RND"i | "RN."i | "R."i) "(" expression ")"
                prompt              :   STRING* VARIABLE
                                    |   STRING ("," STRING)* VARIABLE
                expression          :   sum
                                    |   sum ">" sum  -> greater
                                    |   sum ">=" sum -> greater_equal
                                    |   sum "<" sum  -> less
                                    |   sum "<=" sum -> less_equal
                                    |   sum "=" sum  -> equal
                                    |   sum "#" sum  -> not_equal
                sum                 :   product
                                    |   sum "+" product -> addition
                                    |   sum "-" product -> subtraction
                product             :   atom
                                    |   product "*" atom -> multiply
                                    |   product "/" atom -> division
                atom                :   positive
                                    |   negative
                                    |   "(" expression ")"
                positive            :   "+"? factor
                negative            :   "-" factor
                factor              :   NUMBER
                                    |   VARIABLE
                                    |   array
                                    |   function_abs
                                    |   function_rnd
                VARIABLE            :   /[A-Za-z]/
                array               :   "@" "(" expression ")"
                NUMBER              :   /[0-9]+/
                STRING              :   /[\"][^\"]*[\"]|[\'][^\']*[\']|[\"][^\"]*$|[\'][^\']*$/
                DIGIT.-1            :   /#[0-9]+/
                COMMA               :   ","
                %import common (WS)
                %ignore WS
            ''', parser='lalr', start='statement')

            # リストの解析
            for number in self._lists.keys():
                count = 0
                for statement in self._lists[number].keys():
                    if number not in self._trees:
                        self._trees[number] = dict()
                    tree = lark.parse(self._lists[number][statement])
                    if tree.data == 'statement':
                        if tree.children[0].data == 'command_if':
                            self._trees[number][count] = Tree('statement', [Tree('command_if', [tree.children[0].children[0]])])
                            count = count + 1
                            self._trees[number][count] = tree.children[0].children[1]
                            count = count + 1
                        elif tree.children[0].data == 'command_input':
                            for child in tree.children[0].children:
                                self._trees[number][count] = Tree('statement', [Tree('command_input', [child])])
                                count = count + 1
                        else:
                            self._trees[number][count] = tree
                            count = count + 1

        # 例外
        except Exception as e:
            sys.stderr.write(f'{e}\n')
            return False

        # 解析の完了
        finally:
            pass

        # 終了
        return True

    # コンパイルする
    def _compile(self):
        pass

    # 実行する
    def _execute(self):

        # 実行の設定
        number = self._start
        statement = 0

        # メインループ
        while number > 0:
            number, statement, key = self._process(number, statement)
            if key is not None:
                value = None
                while value is None:
                    string = input()
                    if len(string) > 0:
                        if string[0].isdecimal():
                            value = self._int16(string)
                        elif string[0].isalpha():
                            key = string[0].upper()
                            if key not in self._variables:
                                self._variables[key] = 0
                            value = self._variables[key]
                    if value is None:
                        self._newline()
                self._variables[key] = value
                self._newline()
                number, statement = self._get_next_statement(number, statement)

    # ステートメントを処理する
    def _process(self, number, statement):

        # Visitor の作成
        result = None
        self._log(f'{number}:{statement} >>>')

        # ステートメントの実行
        try:
            result = self.transform(self._trees[number][statement])

        # 例外
        except Exception as e:
            sys.stderr.write('f{e}\n')
            return 0, 0, None

        # 実行の完了
        finally:
            if result[0] == 'else':
                if number in self._nexts:
                    number = self._nexts[number]
                    statement = 0
                else:
                    number = 0
            elif result[0] == 'goto':
                number = result[1]
                statement = 0
            elif result[0] == 'gosub':
                number, statement = self._get_next_statement(number, statement)
                self._gosubs.append([number, statement])
                number = result[1]
                statement = 0
            elif result[0] == 'return':
                params = self._gosubs.pop()
                number = params[0]
                statement = params[1]
            elif result[0] == 'for':
                number, statement = self._get_next_statement(number, statement)
                self._fors.append([number, statement, result[1], result[2], result[3]])
            elif result[0] == 'next':
                if result[1] is not None:
                    number = result[1][0]
                    statement = result[1][1]
                else:
                    number, statement = self._get_next_statement(number, statement)
            elif result[0] == 'stop':
                number = 0
            elif result[0] == 'input':
                pass
            else:
                number, statement = self._get_next_statement(number, statement)

        # 終了
        return number, statement, result[1] if result[0] == 'input' else None

    # Transformer

    # statement
    def statement(self, tree):
        self._log(f'statement: {tree}')
        return tree[0]

    # command_let
    def command_let(self, tree):
        self._log(f'command_let: {tree}')
        return [None, None]

    # let
    def let(self, tree):
        self._log(f'let: {tree}')
        if tree[0][0] == 'VARIABLE':
            self._variables[tree[0][1]] = tree[1][1]
        elif tree[0][0] == 'array':
            self._array[tree[0][1][1]] = tree[1][1]
        return tree[1][1]

    # command_print
    def command_print(self, tree):
        self._log(f'command_print {tree}')
        digit = 6
        cr = True
        for element in tree:
            if element[0] == 'STRING':
                self._print(element[1])
            elif element[0] == 'NUMBER':
                self._print(f'{element[1]:{digit}d}')
            elif element[0] == 'DIGIT':
                digit = element[1]
            elif element[0] == 'COMMA':
                cr = False
            else:
                pass
        if cr:
            self._newline()
        return [None, None]

    # command_input
    def command_input(self, tree):
        self._log(f'command_input {tree}')
        prompt = tree[0]
        if len(prompt) > 1:
            for i in range(len(prompt) - 1):
                self._print(prompt[i][1])
        else:
            self._print(prompt[0][1])
        self._print(':')
        return ['input', prompt[len(prompt) - 1][1]]

    # command_if
    def command_if(self, tree):
        self._log(f'command_if {tree}')
        return [None, None] if tree[0][1] != 0 else ['else', None]
    
    # command_goto
    def command_goto(self, tree):
        self._log(f'command_goto {tree}')
        return ['goto', tree[0][1]]
    
    # command_gosub
    def command_gosub(self, tree):
        self._log(f'command_gosub {tree}')
        return ['gosub', tree[0][1]]
    
    # command_return
    def command_return(self, tree):
        self._log(f'command_return {tree}')
        return ['return', None]
    
    # command_for
    def command_for(self, tree):
        self._log(f'command_for {tree}')
        self._variables[tree[0][1]] = tree[1][1]
        return ['for', tree[0][1], tree[2][1], tree[3][1] if len(tree) >= 4 else 1]
    
    # command_next
    def command_next(self, tree):
        self._log(f'command_next {tree}')
        i = len(self._fors) - 1
        while i >= 0 and self._fors[i][2] != tree[0][1]:
            self._fors.pop()
            i = i - 1
        result = None
        if i >= 0:
            v = self._fors[i][2]
            self._variables[v] = self._int16(self._int16(self._variables[v] + self._fors[i][4]))
            if (self._fors[i][4] > 0 and self._variables[v] <= self._fors[i][3]) or (self._fors[i][4] < 0 and self._variables[v] >= self._fors[i][3]):
                result = [self._fors[i][0], self._fors[i][1]]
        return ['next', result]
    
    # command_stop
    def command_stop(self, tree):
        self._log(f'command_stop: {tree}')
        return ['stop', 0]

    # function_abs
    def function_abs(self, tree):
        self._log(f'function_abs: {tree}')
        return ['NUMBER', abs(tree[0][1])]

    # function_rnd
    def function_rnd(self, tree):
        self._log(f'function_rnd: {tree}')
        return ['NUMBER', random.randint(1, tree[0][1])]

    # prompt
    def prompt(self, tree):
        self._log(f'prompt: {tree}')
        return tree

    # expression
    def expression(self, tree):
        self._log(f'expression: {tree}')
        return tree[0]

    # greater
    def greater(self, tree):
        self._log(f'greater: {tree}')
        return ['NUMBER', 1 if tree[0] > tree[1] else 0]
        
    # greater_equal
    def greater_equal(self, tree):
        self._log(f'greater: {tree}')
        return ['NUMBER', 1 if tree[0] >= tree[1] else 0]
        
    # less
    def less(self, tree):
        self._log(f'less: {tree}')
        return ['NUMBER', 1 if tree[0] < tree[1] else 0]
        
    # less_equal
    def less_equal(self, tree):
        self._log(f'less_equal: {tree}')
        return ['NUMBER', 1 if tree[0] <= tree[1] else 0]
        
    # equal
    def equal(self, tree):
        self._log(f'equal: {tree}')
        return ['NUMBER', 1 if tree[0] == tree[1] else 0]
        
    # not_equal
    def not_equal(self, tree):
        self._log(f'not_equal: {tree}')
        return ['NUMBER', 1 if tree[0] != tree[1] else 0]
        
    # sum
    def sum(self, tree):
        self._log(f'sum: {tree}')
        return tree[0]

    # addition
    def addition(self, tree):
        self._log(f'addition: {tree}')
        return ['NUMBER', self._int16(tree[0][1] + tree[1][1])]

    # subtraction
    def subtraction(self, tree):
        self._log(f'subtraction: {tree}')
        return ['NUMBER', self._int16(tree[0][1] - tree[1][1])]

    # product
    def product(self, tree):
        self._log(f'product: {tree}')
        return tree[0]

    # multiply
    def multiply(self, tree):
        self._log(f'multiply: {tree}')
        return ['NUMBER', self._int16(tree[0][1] * tree[1][1])]

    # division
    def division(self, tree):
        self._log(f'division: {tree}')
        return ['NUMBER', self._int16(tree[0][1] / tree[1][1])]

    # atom
    def atom(self, tree):
        self._log(f'atom: {tree}')
        return tree[0]

    # positive
    def positive(self, tree):
        self._log(f'positive: {tree}')
        # return ['NUMBER', self._int16(tree[0][1])]
        return tree[0]

    # negative
    def negative(self, tree):
        self._log(f'negative: {tree}')
        return ['NUMBER', self._int16(-tree[0][1])]

    # factor
    def factor(self, tree):
        self._log(f'factor: {tree}')
        result = 0
        if tree[0][0] == 'NUMBER':
            result = tree[0][1]
        elif tree[0][0] == 'VARIABLE':
            key = tree[0][1]
            if key not in self._variables:
                self._variables[key] = 0
            result = self._variables[key]
        elif tree[0][0] == 'array':
            key = tree[0][1][1]
            if key not in self._array:
                self._array[key] = 0
            result = self._array[key]
        return ['NUMBER', result]

    # VARIABLE
    def VARIABLE(self, tree):
        self._log(f'VARIABLE: {tree}')
        return ['VARIABLE', tree[0].upper()]

    # array
    def array(self, tree):
        self._log(f'array: {tree}')
        return ['array', tree[0]]

    # NUMBER
    def NUMBER(self, tree):
        self._log(f'NUMBER: {tree}')
        return ['NUMBER', self._int16(tree.value)]

    # STRING
    def STRING(self, tree):
        self._log(f'STRING: {tree}')
        tail = len(tree.value) - 1
        if tree.value[0] == "\"":
            if tree.value[tail] == "\"":
                tail = tail - 1
        elif tree.value[0] == "'":
            if tree.value[tail] == "'":
                tail = tail - 1
        return ['STRING', tree.value[1:tail + 1]]

    # DIGIT
    def DIGIT(self, tree):
        self._log(f'DIGIT: {tree}')
        return ['DIGIT', self._int16(tree.value[1:])]

    # COMMA
    def COMMA(self, tree):
        self._log(f'COMMA: {tree}')
        return ['COMMA', 0]

    # 16bits 整数を取得する
    def _int16(self, value):
        result = value if type(value) is int else int(value)
        result = result & 0xffff
        return result if result < 0x8000 else result - 0x10000

    # 次のステートメントを取得する
    def _get_next_statement(self, number, statement):
        statement = statement + 1
        if statement not in self._trees[number]:
            if number in self._nexts:
                number = self._nexts[number]
                statement = 0
            else:
                number = 0
        else:
            pass
        return number, statement

    # 文字列を出力する
    def _print(self, string):
        print(string, end = '')

    # 改行する
    def _newline(self):
        print('')

    # ログを出力する
    def _log(self, *args):
        if self._debug:
            for value in args:
                print(value, end = '')
            print('')

# アプリケーションのエントリポイント
#
if __name__ == '__main__':

    # 引数の取得
    if len(sys.argv) < 2:
        sys.stderr.write('error - no file.\n')
        exit()
    
    # Tiny BASIC の実行
    TinyBasic().run(sys.argv[1])

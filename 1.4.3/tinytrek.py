# tinytrek.py - TinyTrek
#


# 参照
#
from sys import call_tracing
from tinybasic import TinyBasic
import pyxel


# TinyTrek クラス
#
class TinyTrek(TinyBasic):

    # コンストラクタ
    def __init__(self):

        # super
        super().__init__()

        # 色の初期化
        self._color_text = 9
        self._color_back = 0

        # フォントの初期化
        self._font_size_x = 4
        self._font_size_y = 6

        # スクリーンの初期化
        self._screen_size_x = 64 * self._font_size_x
        self._screen_size_y = 24 * self._font_size_y

        # カーソルの初期化
        self._cursor_x = 0
        self._cursor_y = self._screen_size_y - self._font_size_y

        # Pyxel の初期化
        pyxel.init(self._screen_size_x, self._screen_size_y, caption = 'Tiny Trek', scale = 2)
        pyxel.cls(self._color_back)

    # 文字列を出力する
    def _print(self, string):

        # １文字ずつ出力
        for c in string:
            self._putc(c)

    # １文字を出力する
    def _putc(self, c, flush = False):

        # １文字の出力
        pyxel.text(self._cursor_x, self._cursor_y, c, self._color_text)

        # カーソルの更新
        self._cursor_x = self._cursor_x + self._font_size_x
        if self._cursor_x >= self._screen_size_x:
            self._newline()
        elif flush:
            pyxel.flip()

    # 改行する
    def _newline(self):

        # スクロール
        pyxel.image(4, system = True).copy(0, 0, 4, 0, self._font_size_y, self._screen_size_x, self._screen_size_y - self._font_size_y)
        pyxel.rect(0, self._screen_size_y - self._font_size_y, self._screen_size_x, self._font_size_y, self._color_back)
        pyxel.flip()

        # カーソルの更新
        self._cursor_x = 0

    # キー入力を受け付ける
    def _input(self):

        # キーコード
        numbers = {
            pyxel.KEY_0: '0', 
            pyxel.KEY_1: '1', 
            pyxel.KEY_2: '2', 
            pyxel.KEY_3: '3', 
            pyxel.KEY_4: '4', 
            pyxel.KEY_5: '5', 
            pyxel.KEY_6: '6', 
            pyxel.KEY_7: '7', 
            pyxel.KEY_8: '8', 
            pyxel.KEY_9: '9', 
        }
        alphabets = {
            pyxel.KEY_A: 'A', 
            pyxel.KEY_B: 'B', 
            pyxel.KEY_C: 'C', 
            pyxel.KEY_D: 'D', 
            pyxel.KEY_E: 'E', 
            pyxel.KEY_F: 'F', 
            pyxel.KEY_G: 'G', 
            pyxel.KEY_H: 'H', 
            pyxel.KEY_I: 'I', 
            pyxel.KEY_J: 'J', 
            pyxel.KEY_K: 'K', 
            pyxel.KEY_L: 'L', 
            pyxel.KEY_M: 'M', 
            pyxel.KEY_N: 'N', 
            pyxel.KEY_O: 'O', 
            pyxel.KEY_P: 'P', 
            pyxel.KEY_Q: 'Q', 
            pyxel.KEY_R: 'R', 
            pyxel.KEY_S: 'S', 
            pyxel.KEY_T: 'T', 
            pyxel.KEY_U: 'U', 
            pyxel.KEY_V: 'V', 
            pyxel.KEY_W: 'W', 
            pyxel.KEY_X: 'X', 
            pyxel.KEY_Y: 'Y', 
            pyxel.KEY_Z: 'Z'
        }

        # 文字列の初期化
        string = ''

        # ENTER が押されるまで
        enter = True
        while enter:

            # ENTER の入力
            if pyxel.btnp(pyxel.KEY_ENTER):
                enter = False

            # BACKSPACE, DELETE の入力
            elif pyxel.btnp(pyxel.KEY_BACKSPACE) or pyxel.btnp(pyxel.KEY_DELETE):
                if len(string) > 0:
                    string = string[:-1]
                    self._cursor_x = self._cursor_x - self._font_size_x
                    pyxel.rect(self._cursor_x, self._cursor_y, self._font_size_x, self._font_size_y, self._color_back)

            # その他の入力
            else:

                # 数値の入力
                for key in numbers:
                    if pyxel.btnp(key):
                        if len(string) < 3:
                            c = numbers[key]
                            string = string + c
                            self._putc(c)

                # アルファベットの入力
                for key in alphabets:
                    if pyxel.btnp(key):
                        if len(string) == 0:
                            c = alphabets[key]
                            string = c
                            self._putc(c)
                            enter = False

            # 画面の更新
            pyxel.flip()

        # 改行
        self._newline()

        # 文字列の確認
        result = None
        if len(string) > 0:
            if string.isdecimal():
                result = self._int16(string)
            elif string[0].isalpha():
                key = string[0].upper()
                if key not in self._variables:
                    self._variables[key] = 0
                result = self._variables[key]

        # 終了
        return result

# アプリケーションのエントリポイント
#
if __name__ == '__main__':

    # Tiny BASIC の実行
    try:
        TinyTrek().run("./tinytrek.bas")
    except Exception as e:
        pass

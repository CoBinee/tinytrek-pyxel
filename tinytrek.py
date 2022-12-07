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

        # 入力の初期化
        self._input_string = ''

        # Pyxel の初期化
        pyxel.init(self._screen_size_x, self._screen_size_y, title = 'Tiny Trek')
        pyxel.cls(self._color_back)
        pyxel.image(0).cls(self._color_back)

    # 実行する
    def _execute(self):

        # 実行の初期化
        self._number = self._start
        self._statement = 0
        self._key = None
        self._speed = 1000

        # Pyxel の実行
        pyxel.run(self._update, self._draw)

    # 1 フレームの更新を行う
    def _update(self):

        # 1 回の更新
        if self._key is None:
            cycle = 0
            while cycle < self._speed and self._key is None:
                self._number, self._statement, self._key = self._process(self._number, self._statement)
                cycle = cycle + 1
            self._input_string = ''

        # キー入力
        if self._key is not None:

            # キー入力の更新
            if self._input():

                # 値の取得
                if self._input_string[0].isdecimal():
                    value = self._int16(self._input_string)
                elif self._input_string[0].isalpha():
                    key = self._input_string[0].upper()
                    if key not in self._variables:
                        self._variables[key] = 0
                    value = self._variables[key]

                # 値の設定
                self._variables[self._key] = value
                self._number, self._statement = self._get_next_statement(self._number, self._statement)
                self._key = None

                # 改行
                self._newline()

        pyxel.blt(0, 0, 0, 0, 0, self._screen_size_x, self._screen_size_y)

    # 1 フレームの描画を行う
    def _draw(self):
        pass

    # 文字列を出力する
    def _print(self, string):

        # １文字ずつ出力
        for c in string:
            self._putc(c)

    # １文字を出力する
    def _putc(self, c, flush = False):

        # １文字の出力
        pyxel.image(0).text(self._cursor_x, self._cursor_y, c, self._color_text)

        # カーソルの更新
        self._cursor_x = self._cursor_x + self._font_size_x
        if self._cursor_x >= self._screen_size_x:
            self._newline()
        # elif flush:
        #     pyxel.flip()

    # 改行する
    def _newline(self):

        # スクロール
        pyxel.image(0).blt(0, 0, 0, 0, self._font_size_y, self._screen_size_x, self._screen_size_y - self._font_size_y)
        pyxel.image(0).rect(0, self._screen_size_y - self._font_size_y, self._screen_size_x, self._font_size_y, self._color_back)
        # pyxel.flip()

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
            pyxel.KEY_KP_0: '0', 
            pyxel.KEY_KP_1: '1', 
            pyxel.KEY_KP_2: '2', 
            pyxel.KEY_KP_3: '3', 
            pyxel.KEY_KP_4: '4', 
            pyxel.KEY_KP_5: '5', 
            pyxel.KEY_KP_6: '6', 
            pyxel.KEY_KP_7: '7', 
            pyxel.KEY_KP_8: '8', 
            pyxel.KEY_KP_9: '9', 
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

        # ENTER が押されるまで
        result = False

        # ENTER の入力
        if pyxel.btnp(pyxel.KEY_RETURN) or pyxel.btnp(pyxel.KEY_KP_ENTER):
            if len(self._input_string) > 0:
                result = True

        # BACKSPACE, DELETE の入力
        elif pyxel.btnp(pyxel.KEY_BACKSPACE) or pyxel.btnp(pyxel.KEY_DELETE):
            if len(self._input_string) > 0:
                self._input_string = self._input_string[:-1]
                self._cursor_x = self._cursor_x - self._font_size_x
                pyxel.image(0).rect(self._cursor_x, self._cursor_y, self._font_size_x, self._font_size_y, self._color_back)

        # その他の入力
        else:

            # 数値の入力
            for key in numbers:
                if pyxel.btnp(key):
                    if len(self._input_string) < 8:
                        c = numbers[key]
                        self._input_string = self._input_string + c
                        self._putc(c)

            # アルファベットの入力
            for key in alphabets:
                if pyxel.btnp(key):
                    if len(self._input_string) == 0:
                        c = alphabets[key]
                        self._input_string = c
                        self._putc(c)

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

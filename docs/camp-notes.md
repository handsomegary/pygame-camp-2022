# Pygame 營隊重點整理

這份筆記依據資料夾內的 5 份營隊 PDF，整理遊戲開發會實際用到的內容，並對照本 repo 的可執行程式。它是重點摘要與實作說明，不是逐頁謄寫講義。變數命名、四則運算、`print()`、`input()`、基本 `if / for / while`、字串操作，以及容器方法清單都省略。

原始 PDF 沒有上傳到 repo；下列檔名和頁次方便回查本機講義。貓咪、棋盤、果實與音效由本專案自行繪製或合成，不包含講義原本使用的圖片、錄音或背景音樂。

## 5 份講義的整理範圍

| 原始講義 | 保留的重點與講義頁次 | 本 repo 對應 |
| --- | --- | --- |
| `PYTHON__part1.pdf` | 函式拆分與模組化（44-48）；遞迴停止條件（49-55），轉化為遊戲流程與食物生成的設計 | [Popcat](../games/popcat.py)、[Snake](../games/snake.py) |
| `PYTHON__part2.pdf` | 容器的選擇：有順序的蛇身、不可變座標、佔用格集合（4、20-32、37-51）；亂數（52-53） | [SnakeGame](../games/snake.py)、[PopcatState](../games/popcat.py) |
| `Class.pdf` | 實例各自持有可變資料（11-13）；繼承（14-21）；覆寫與多型（22-25），補充 Python 中多載與封裝的差異 | 本文「狀態與物件」；選讀 [classes.py](../examples/classes.py) |
| `pygame__popcat.pdf` | 視窗、Surface、圖片、文字、聲音（5-13）；事件（14-17）；按下加分、張嘴與放開閉嘴（18-28）；兩隻會動的貓（29-37） | [Popcat 完整實作](../games/popcat.py) |
| `snake.pdf` | 格子移動與轉彎（6-20）；果實、成長、碰撞（21-30）；物件、計分與重開（31-42）；畫布、透明度、文字與音效（43-58） | [Snake 完整實作](../games/snake.py) |

建議直接從 [games/popcat.py](../games/popcat.py) 的 `PopcatState`、`run()` 開始，再看 [games/snake.py](../games/snake.py) 的 `SnakeGame`、`run()`。不需要先跑一整套 Python 入門練習。

## Pygame 的主迴圈

### 初始化與關閉

一次遊戲的生命週期是：設定音訊參數、`pygame.init()`、建立視窗與字型、建立狀態與畫面素材、進入主迴圈，最後 `pygame.quit()`。

`pygame.display.set_mode((width, height))` 建立視窗，回傳用來繪圖的 Surface。一般 Surface 是離螢幕畫布；`blit()` 把一張 Surface 畫到另一張 Surface 上。`screen.fill()` 清除上一幀，再依順序繪製背景、角色、計分與提示，最後 `pygame.display.flip()` 顯示這一幀。

兩個遊戲的 `run()` 都用 `try / finally` 清理 Pygame。由 `python main.py` 選單啟動時，按 Esc 或關閉遊戲視窗會結束該遊戲的 `run()`，由 [main.py](../main.py) 接回選單；選單需要重新初始化顯示與字型，不能繼續使用遊戲 `pygame.quit()` 前的 Surface。直接以 `--game` 啟動或執行遊戲模組時，離開後會結束程式。

### 處理事件、更新狀態、繪圖

每一幀依序完成三件事：

1. 讀取本幀事件，處理按下、放開、關閉視窗與失去焦點。
2. 依經過時間更新模型，例如移動貓咪，或讓蛇前進一格。
3. 把更新後的狀態畫出來，刷新畫面。

概念流程如下，省略實際的視窗與字型設定：

```text
初始化資源與遊戲狀態
while 遊戲仍在執行:
    計算距離上一幀的時間
    依序處理 event.get() 取出的事件
    若收到離開指令，結束迴圈
    更新遊戲狀態
    清除畫面、畫背景、畫角色、畫文字
    flip()
清理 Pygame 資源
```

`pygame.event.get()` 取出並移除事件佇列中的事件，預設也會執行 pump。正常每幀都有呼叫 `event.get()` 時，不必再加 `event.pump()`。佇列有容量上限，因此應維持每幀處理事件，而不是長時間阻塞後才一次處理。`snake.pdf` 第 19-20 頁以 pump 分散負擔的說法，不作為本實作的速度控制方式。[Pygame 事件文件](https://www.pygame.org/docs/ref/event.html)

事件和「目前按住」的狀態適合不同用途。Popcat 每次新按下才加一分，因此使用 down / up 事件；蛇使用方向事件排入待執行的轉彎，不把「按住某鍵」解讀成每一幀都新增轉彎。

不要在遊戲主迴圈裡呼叫等待輸入的 `input()`，或放入長時間的 `sleep()` / `delay()`。等待期間沒有處理視窗事件，玩家會覺得遊戲沒有反應。

### 繪圖速度與遊戲速度分開

兩個遊戲用 `Clock.tick(60)` 限制繪圖頻率的目標上限；它不保證機器一定能達到 60 FPS。回傳的毫秒轉換成秒後，就是該幀的時間差。[Pygame 時間文件](https://www.pygame.org/docs/ref/time.html)

- Popcat 移動模式：`x += vx * dt`、`y += vy * dt`，速度以每秒像素表示。換電腦或幀率降低時，不會因為「每幀加固定像素」而任意改變速度。
- Snake：畫面與事件處理以 60 FPS 為目標；移動另外累積時間，每滿 `0.1` 秒才 `tick()` 一次，維持講義每秒走 10 格的節奏。

兩個遊戲會限制單幀採用的時間差（Popcat 0.05 秒、Snake 0.1 秒），避免切換視窗或暫時卡頓後角色瞬間跳太遠。這個選擇會捨棄超出的時間，並不保證長時間卡頓後完整補跑所有移動。

## Popcat：從單隻到兩隻會動的貓

### 講義要求與本 repo 的行為

`pygame__popcat.pdf` 第 19 頁規則是：按下貓咪，加分、張嘴、播放「啵」；放開滑鼠，閉嘴。第 37 頁挑戰是兩隻會動的貓。這兩個部分均實作在 [games/popcat.py](../games/popcat.py)。

| 操作 | 行為 |
| --- | --- |
| 滑鼠左鍵按下貓咪 | 該貓加一分、張嘴、觸發音效與短暫動畫 |
| 左鍵放開 | 釋放當初按下的貓，滑鼠移出貓的範圍也能閉嘴 |
| Space / Enter | 操作第一隻貓；按下加分，放開釋放該按鍵 |
| Tab | 切換單隻固定貓與兩隻移動貓，並重設分數與位置 |
| R | 重設目前模式的分數與狀態 |
| M | 切換音效開關 |
| Esc | 返回選單 |

單隻模式顯示第一隻貓的分數；雙貓模式顯示各自分數與總分。雙貓各自持有位置、速度及 `PopcatState`，到移動區域邊界時反彈。Space / Enter、模式切換、重設、靜音、動畫與返回選單是本 repo 的操作補充。

### 用輸入集合表示張嘴狀態

`PopcatState` 儲存 `clicks` 與 `_held_inputs`。嘴巴是否張開，取決於是否仍有任何輸入按住：

```text
新輸入按下:
    若該輸入已在 held_inputs，忽略重複的 down
    否則加入 held_inputs、分數加一、播放音效
某輸入放開:
    從 held_inputs 移除該輸入
mouth_open = held_inputs 是否非空
```

例如先按住滑鼠，再按住 Space，嘴巴保持張開；放開滑鼠時 Space 還按著，所以仍張嘴。若只用一個布林值，收到任一 release 就關嘴，會錯誤處理這種多輸入情況。同一個輸入的重複 down 不重複加分，不同輸入的新按下則各加一次。

滑鼠命中判定先檢查貓咪矩形，再檢查該像素的 alpha，透明區域不算按中；兩隻貓重疊時，後繪製的那隻先接收點擊。`active_mouse` 記住當初按中的貓，避免貓移動後放開滑鼠時釋放錯誤的物件。

失去視窗焦點會清空全部 held inputs，避免玩家切到其他應用程式放開按鍵，遊戲收不到 up 事件而一直張嘴。Tab / R 同樣會釋放舊輸入，讓新模式與新回合從乾淨狀態開始。

## Snake：格子規則與邊界情況

### 座標與資料結構

講義的遊戲畫布為 720 × 630 像素，單格 30 像素，對應 24 欄 × 21 列。本 repo 維持這個棋盤大小與初始長度 3；外層視窗是 780 × 810，額外空間放計分、標題與操作提示。

`SnakeGame` 儲存格子座標，不直接儲存畫面像素。`Cell = tuple[int, int]`，例如 `(3, 5)` 是第 3 欄、第 5 列；繪製時才轉換為 `board.x + x * 30`、`board.y + y * 30`。這樣牆壁與食物判定不必混入標題列高度或視窗邊界。

`body` 是從頭到尾排序的 list，`body[0]` 就是蛇頭。不能改成 set 儲存整條蛇，因為需要知道哪一段是尾巴。`set(body)` 則適合暫時查詢哪些格子已佔用，以便選擇食物位置。

`snake.pdf` 第 14-15 頁提醒不要把同一個可變 list 重複插入蛇身。`list(a)` / `a.copy()` 只是淺拷貝，巢狀可變物件仍可能共享。本實作以只包含整數的 tuple 儲存每一格，前進時建立新 tuple，避免改蛇頭時連帶改掉其他節的位置。

### 快速轉彎與禁止反向

`Direction` 以 `(dx, dy)` 表示上下左右。`request_direction()` 最多緩存兩次合法轉彎，`tick()` 每次只消耗一次；不接受和參考方向相同或相反的輸入。

判斷新輸入時，參考的是「佇列中最後一次轉彎」，沒有排隊轉彎才參考目前行進方向。向右行進時快速按上、左，會在接下來兩次移動依序往上、往左；不能把兩次方向立刻覆蓋成向左，否則蛇尚未移動就直接反向撞到自己。

移動頻率與事件頻率分開，因此兩次 `tick()` 之間仍能接收按鍵、暫停或關閉視窗。

### 每一步的更新順序

[SnakeGame.tick()](../games/snake.py) 的概念流程是：

```text
若已輸或已贏，停止更新
取出至多一次排隊轉彎
計算 new_head
判斷 new_head 是否是食物
依本次是否成長決定哪些身體格仍被佔用
若撞牆或撞到仍被佔用的身體，轉為 LOST
將 new_head 插到蛇身最前方
若吃食物: 加一分、保留尾巴、生成新食物
否則: 移除尾巴
```

這對應講義第 26 頁「先伸長再縮短；吃到食物時不縮短」的做法。吃一顆食物長一格，也加一分。

碰撞有一個容易忽略的例外：沒有吃到食物的這一步，舊尾巴會移走，因此蛇頭可以移入該尾巴目前所在格。本實作比較 `body[:-1]`；若本步成長，尾巴留下，就必須比較整個 `body`。牆壁則以 `0 <= x < columns`、`0 <= y < rows` 判斷。

### 食物生成與滿版通關

講義第 29-30 頁的做法是隨機生成座標，與蛇身重疊就再遞迴抽一次。蛇很長時可能重試很多次；全棋盤被佔滿時，更沒有能成功返回的座標。

本 repo 的 `spawn_fruit()` 先列出所有空格，再用 `rng.choice(free)` 選一格。沒有空格時，明確設定 `fruit = None`、`state = WON`。這保留第 3 頁的滿版通關規則，也避免無限重抽。

這裡的 `[... for ... if ...]` 是 list comprehension，會建立空格 list；`snake.pdf` 第 24 頁稱它為 generator 並不精確。真正的 generator expression 使用圓括號，且逐項產生值。[Python 資料結構文件](https://docs.python.org/3.12/tutorial/datastructures.html)

模型可傳入 `random.Random(seed)` 以重現食物序列。相同種子與相同操作順序可用來定位錯誤；一般遊玩不固定種子。`reset()` 保留原亂數產生器，重新開始不代表重新播同一份食物序列。

### 回合、暫停與離開

模型狀態為 `RUNNING`、`LOST`、`WON`；`run()` 額外管理準備畫面和暫停畫面。它們不改寫蛇身規則。方向鍵 / WASD 操作，Space / P 暫停或繼續，R 重開，Enter 開始或在結束後重開，M 靜音，Esc 返回選單。

失去焦點會自動暫停進行中的遊戲；繼續或重開時清除累積時間，避免一恢復就補走舊的步數。最高分只保留在這次開啟 Snake 的 session，沒有寫入磁碟，返回選單再開 Snake 會重新計算。

講義第 38-42 頁以外層迴圈重開；本 repo 直接呼叫 `model.reset()`，清除蛇身、方向佇列、分數與碰撞狀態。結束一局、重開與離開遊戲是不同操作，不需要遞迴呼叫 `run()`，也不需要用 `exit()` 關閉整個選單程式。

## 狀態與物件：保留會影響遊戲的 Class 重點

`Class.pdf` 第 11-13 頁的核心是各實例的可變資料必須獨立。如果把蛇身或按住的輸入放成共用的類別 list / set，開兩個模型就可能互相改動。

- `SnakeGame.__init__()` 為每個物件建立自己的 `body` 和 `_turns`。
- `PopcatState` 使用 `field(default_factory=set)`，每次建構時產生新 set。
- `_Cat` 將一隻貓的狀態、位置、速度及動畫數值放在一起；兩隻貓分別建立自己的 `PopcatState()`。

`default_factory` 接收的是建構函式 `set`，不是預先建立的 `set()`；目的正是避免實例共享同一份資料。[dataclasses 文件](https://docs.python.org/3.12/library/dataclasses.html)

`SnakeGame` 的規則不依賴 Pygame；只測試 `reset()`、`request_direction()`、`tick()` 就能檢查成長、碰撞和通關。`run()` 負責把事件轉成模型操作、把模型畫出來。這是 `PYTHON__part1.pdf` 函式拆分與 `Class.pdf` 資料和行為結合的實際用途。

講義 `snake.pdf` 第 36 頁說函式不能直接修改外部變數，需區分「修改物件內容」和「重新綁定名稱」：函式可以修改傳入的 mutable 物件；重綁外層名稱才涉及 `global` / `nonlocal`。方法操作 `self` 屬性是把狀態整理在同一個物件內，不是唯一能修改資料的方式。[Python 類別與作用域文件](https://docs.python.org/3.12/tutorial/classes.html)

繼承與覆寫可選讀 [examples/classes.py](../examples/classes.py)，執行 `python -m examples.classes`：`Dog`、`Cat` 覆寫 `Animal.talk()`，同一種呼叫依物件得到不同結果；兩隻狗的技能 list 不會互相污染。遊戲本身沒有為了展示繼承而建立複雜的類別階層。

`Class.pdf` 第 22-24 頁的多載說法需補充：Python 同一作用域重複定義同名 `def`，後面的會取代前面的，不會自動依參數個數或型別挑選版本。覆寫父類別方法則可以照講義運作。`__name` 的名稱改寫主要避免子類別撞名，不是禁止外界存取；`_name` 是內部使用慣例。多重繼承查找依 MRO，也不是一律先走完整個左側父類別。[Python 類別文件](https://docs.python.org/3.12/tutorial/classes.html)

## 畫面、文字與聲音

Popcat 建立兩組「閉嘴 / 張嘴」Surface，先畫大圖再縮小，遊戲迴圈依 `mouth_open` 選擇其中一張。Snake 用矩形、圓形和線條直接繪出棋盤、蛇與食物。角色、分數和規則保持分離，換圖片不需要改碰撞或計分。

透明效果使用 `pygame.Surface(size, pygame.SRCALPHA)`：Popcat 的角色背景與點擊光圈、Snake 暫停與結束時的半透明遮罩都用到 alpha。講義介紹 `convert_alpha()` 是載入含透明度圖片時的另一種常見做法；本 repo 沒有外部圖片載入流程。

文字先經 `font.render()` 轉成 Surface，再以 `get_rect(center=...)`、`topleft`、`topright` 等錨點定位，對應 `snake.pdf` 第 53-56 頁。Popcat 使用 Pygame 內建字型；Snake 請求系統 Segoe UI，找不到時由 Pygame 選擇可用字型。遊戲介面採英文，中文操作與設計說明在 [README](../README.md) 及本文。

音效以 Python `array('h')` 建立 16-bit PCM samples，再交給 `pygame.mixer.Sound(buffer=...)`。Popcat 合成短促的下降音；Snake 使用不同音符組合區分吃果實、失敗和勝利。沒有背景音樂。音訊初始化不可用時仍可遊玩，M 可靜音；這與講義的媒體功能相對應，但聲音內容為重新製作。

若日後改成檔案素材，建議由程式檔案位置解析素材路徑，再處理載入失敗；不要依賴玩家從哪個目錄啟動。換字型或圖片也應保留現在的無音訊可用行為。

## 可以直接動手改的地方

| 想改什麼 | 先閱讀的位置 | 要一起考慮的事情 |
| --- | --- | --- |
| Popcat 角色顏色 / 外觀 | `_make_cat_surface()`、`PEACH`、`GOLD` | 滑鼠命中會使用角色矩形與 alpha |
| 兩隻貓的移動速度 / 範圍 | Popcat `reset()` 與主迴圈移動段落 | 使用每秒像素與 dt；範圍要留角色尺寸的空間 |
| 蛇每秒移動幾格 | Snake `run()` 的 `0.1` 秒移動間隔 | 減少間隔會提高難度；不要連同事件處理降成每秒幾次 |
| 初始蛇長與模型棋盤大小 | `SnakeGame(columns, rows, initial_length=...)` | 模型支援調整；目前畫面是 24 × 21、30 像素一格，改模型尺寸也要改 `board` 與繪圖配置 |
| 增加新的遊戲提示 / 音效 | Snake `draw_overlay()`、`_make_sounds()` | 提示不應改動模型規則；音效仍需允許不可用 |

修改規則後，可從 repo 根目錄執行 `python -m unittest discover -s tests -v`。規則測試不需要開視窗；畫面、按鍵和音訊仍需實際開啟遊戲檢查。

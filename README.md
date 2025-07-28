# Sundrop Caves 🪓⛏️

**Sundrop Caves** is a text-based strategy RPG where you explore deep underground mines to collect valuable ores, complete quests, and earn enough gold pieces (GP) to retire in glory.

## 🎯 Objective

Earn **100 GP** by mining, selling ores, and completing quests. Upgrade your equipment and dive deeper into the cave system to find rarer minerals.

---

## 🕹️ How to Play

### Controls
- Use `W`, `A`, `S`, `D` to move in the mine
- Press `P` to return to town using your portal
- Access map, player info, shop, and quest board from the town menu

---

## 🧱 Game Structure

### Floors
- **Level 1:** Basic ores (Copper, Silver, Gold)
- **Level 2:** Adds **Platinum** and more Gold clusters
- **Level 3:** Introduces **Obsidian**, the rarest ore

### Navigation
- `D` tile: Door to go **down**
- `U` tile: Door to go **up**
- `T` tile: Teleports you back to town (portal)

---

## ⛏️ Ores & Mining

| Ore       | Symbol | Appears On    | Value (GP)    | Yield |
|-----------|--------|---------------|---------------|--------|
| Copper    | `C`    | All levels     | 1–3           | 1–5    |
| Silver    | `S`    | All levels     | 5–8           | 1–3    |
| Gold      | `G`    | All levels     | 10–18         | 1–2    |
| Platinum  | `P`    | Levels 2 & 3   | 15–25         | 1–2    |
| Obsidian  | `O`    | Level 3 only   | 30–50         | 1      |

Use better pickaxes to mine more valuable ores:
- Level 1: Copper only
- Level 2: Copper + Silver
- Level 3: + Gold
- Level 4: + Platinum
- Level 5: + Obsidian

---

## 📋 Quests

Quests are given at the **quest board**. They can include:
- Mining a specific ore
- Taking a number of steps
- Reaching a level you haven’t been to recently

If you don’t like your quest, you can cancel and get a new one.

---

## 💾 Saving and Loading

Progress can be saved to and loaded from `savegame.json`. Save often!

---

## 🏁 Winning

Earn **100 GP** and you’ll retire a hero of the mines. Your score is recorded based on **days taken** and **steps walked**.

---

## 🛠️ Setup

Ensure the following files exist:

. S10270880E_Assignment.py
. level1.txt
. level2.txt
. level3.txt

---

No external libraries needed — just run:
```bash
python S10270880E_Assignment.py
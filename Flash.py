from flask import Flask, request, jsonify, send_file
import requests
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import os

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=12)
session = requests.Session()

# ================================
# [★] FLASH OUTFIT API
# [★] DEVELOPED BY: FLASH
# ================================

API_KEYS = ["Flash2hour", "DENGER"]  # Add multiple keys: ["FLASH", "key2"]
BACKGROUND_FILENAME = "Flash.png"
CANVAS_SIZE = (860, 860)
IMAGE_TIMEOUT = 8

# --- SERVERS (Auto-try order) ---
SERVERS = ["sg", "br", "me", "pk", "ind", "us", "sac", "cis", "bd", "tw", "th"]

# --- ICON API ---
ICON_URL = "https://cdn.jsdelivr.net/gh/ShahGCreator/icon@main/PNG/{item_id}.png"

# --- OUTFIT CATEGORIES ---
# IMPORTANT: Mask must come BEFORE Head!
# Both use "211" prefix and in equipedskills list
# mask ID (211036xxx) comes before head ID (211000xxx).
# Via used_ids mechanism:
#   - First "211" match → Mask
#   - Second "211" match → Head
OUTFIT_SLOTS = [
    {
        "name": "Head",
        "prefix": "211",
        "default": "211000000",
        "pos": {'x': 350, 'y': 45, 'width': 150, 'height': 150} # Top
    },
    {
        "name": "Face Paint",
        "prefix": "214",
        "default": "214000000",
        "pos": {'x': 595, 'y': 125, 'width': 150, 'height': 150} # Top Right
    },
    {
        "name": "Mask",
        "prefix": "211",
        "default": "208000000",
        "pos": {'x': 675, 'y': 335, 'width': 150, 'height': 150} # Right
    },
    {
        "name": "Top",
        "prefix": "203",
        "default": "203000000",
        "pos": {'x': 590, 'y': 553, 'width': 150, 'height': 150} # Bottom Right
    },
    {
        "name": "Bottom",
        "prefix": "204",
        "default": "204000000",
        "pos": {'x': 350, 'y': 650, 'width': 150, 'height': 150} # Bottom
    },
    {
        "name": "Shoes",
        "prefix": "205",
        "default": "205000000",
        "pos": {'x': 115, 'y': 545, 'width': 150, 'height': 150} # Bottom Left
    },
    {
        "name": "Weapon",
        "prefix": "907",
        "default": None, 
        "pos": {'x': 35, 'y': 345, 'width': 150, 'height': 150} # Left (Khali Octagon)
    },
    {
        "name": "Bundle",
        "prefix": "203",
        "default": "212000000",
        "pos": {'x': 115, 'y': 125, 'width': 150, 'height': 150} # Top Left
    }
]

def remove_black_background(img):
    img = img.convert("RGBA")
    datas = img.getdata()
    new_data = []
    for item in datas:
        if item[0] == 0 and item[1] == 0 and item[2] == 0:
            new_data.append((0, 0, 0, 0))
        else:
            new_data.append(item)
    img.putdata(new_data)
    return img

def fetch_player_info(uid: str, region: str = None):
    # Agar region diya gaya hai, toh sirf wahi check karega
    # Agar nahi diya gaya, toh purani list (SERVERS) use karega
    target_servers = [region] if region else SERVERS
    
    for server in target_servers:
        try:
            url = f"https://flash-player-info.vercel.app/info?uid={uid}&key=Flash"
            resp = session.get(url, timeout=IMAGE_TIMEOUT)
            if resp.status_code == 200:
                data = resp.json()
                if data and isinstance(data, dict):
                    if data.get("error") or data.get("status") == "error":
                        continue
                    profile = data.get("profileInfo", {})
                    # Check for clothes array in profileInfo
                    if profile.get("clothes"):
                        print(f"  [✓] Server found: {server} (UID: {uid})")
                        return data
                    if data.get("basicInfo") or data.get("profileInfo"):
                        print(f"  [✓] Server found: {server} (UID: {uid}) - Outfit data may be missing")
                        return data
        except Exception:
            continue
    return None


def extract_outfit_ids(player_data: dict) -> list:
    """Extract equipped item IDs from player data.
    
    API response format:
      profileInfo.clothes: [203000482, 211000049, 214041002, 205000059, 204000181, 211000017]
        → top, head/mask, face paint, shoes, bottom, head/mask
      basicInfo.weaponSkinShows: [912049002]
        → weapon/loot crate
    """
    if not player_data:
        return []

    # 1. Outfit IDs (profileInfo.clothes) - FIXED: Changed from equipedskills to clothes
    outfit_ids = []
    profile = player_data.get("profileInfo", {})
    if profile.get("clothes"):
        outfit_ids = profile.get("clothes", [])
    
    # Also check other possible locations
    if not outfit_ids:
        outfit_ids = (
            player_data.get("profileinfo", {}).get("clothes") or
            player_data.get("AccountProfileInfo", {}).get("Clothes") or
            []
        )

    if isinstance(outfit_ids, dict):
        outfit_ids = list(outfit_ids.values())

    all_ids = [str(oid) for oid in outfit_ids if oid]

    # 2. Weapon & Animation IDs (basicInfo.weaponSkinShows) - FIXED: Changed from weaponskinshows to weaponSkinShows
    weapon_ids = player_data.get("basicInfo", {}).get("weaponSkinShows", [])
    if isinstance(weapon_ids, dict):
        weapon_ids = list(weapon_ids.values())
    for wid in weapon_ids:
        str_wid = str(wid)
        if str_wid not in all_ids:
            all_ids.append(str_wid)

    print(f"  [i] Extracted IDs: {all_ids}")
    return all_ids


def fetch_icon_image(item_id: str):
    """Download a single item icon."""
    url = ICON_URL.format(item_id=item_id)
    try:
        resp = session.get(url, timeout=IMAGE_TIMEOUT)
        if resp.status_code == 200:
            return Image.open(BytesIO(resp.content)).convert("RGBA")
    except Exception:
        pass
    return None


def find_item_for_slot(slot: dict, outfit_ids: list, used_ids: set) -> str | None:
    """Find appropriate item ID for a slot."""
    prefix = slot["prefix"]

    # Search for matching category in player's equipped items
    for oid in outfit_ids:
        if oid.startswith(prefix) and oid not in used_ids:
            used_ids.add(oid)
            return oid

    # If not found, use default (if available)
    if slot["default"]:
        return slot["default"]

    return None


@app.route('/outfit', methods=['GET'])
def make_outfit():
    uid = request.args.get('uid')
    key = request.args.get('key')
    region = request.args.get('region') # Naya parameter

    if key not in API_KEYS:
        return jsonify({'error': 'Invalid API Key', 'status': 'unauthorized'}), 401
    
    if not uid:
        return jsonify({'error': 'Missing uid parameter', 'status': 'bad_request'}), 400

    
    print(f"[*] Generating outfit: UID={uid} | Region={region or 'All'}")
    
    player_data = fetch_player_info(uid, region) 
    
    if not player_data:
        return jsonify({'error': f'Player not found in {region or "any region"}', 'status': 'not_found'}), 404

    # 2. Extract equipped item IDs
    outfit_ids = extract_outfit_ids(player_data)
    print(f"  [i] Outfit IDs found: {len(outfit_ids)}")
    if outfit_ids:
        print(f"  [i] IDs: {outfit_ids}")

    # 3. Find matching item for each slot and download icons in parallel
    used_ids = set()
    download_tasks = []

    for slot in OUTFIT_SLOTS:
        item_id = find_item_for_slot(slot, outfit_ids, used_ids)
        if item_id:
            future = executor.submit(fetch_icon_image, item_id)
            download_tasks.append((slot, future, item_id))
        else:
            print(f"  [~] {slot['name']}: Skipped (no item)")

    # 4. Open background image
    bg_path = os.path.join(os.path.dirname(__file__), BACKGROUND_FILENAME)
    try:
        background = Image.open(bg_path).convert("RGBA")
    except FileNotFoundError:
        return jsonify({'error': f'{BACKGROUND_FILENAME} not found! Place it in the OUTFIT folder.'}), 500
    except Exception as e:
        return jsonify({'error': f'Background error: {str(e)}'}), 500

    # Create canvas
    canvas_w, canvas_h = CANVAS_SIZE if CANVAS_SIZE else background.size
    bg_resized = background.resize((canvas_w, canvas_h), Image.LANCZOS)
    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    canvas.paste(bg_resized, (0, 0))

    # 5. Process and paste downloaded icons at their coordinates
    for slot, future, item_id in download_tasks:
        icon_img = future.result()
        if icon_img:
            # Remove black background from the icon
            icon_img = remove_black_background(icon_img)
            
            pos = slot["pos"]
            icon_resized = icon_img.resize((pos['width'], pos['height']), Image.LANCZOS)
            paste_y = max(0, pos['y'])
            canvas.paste(icon_resized, (pos['x'], paste_y), icon_resized)
            print(f"  [✓] {slot['name']}: {item_id}")
        else:
            print(f"  [✗] {slot['name']}: Icon download failed ({item_id})")

    # 6. Send as PNG
    output = BytesIO()
    canvas.save(output, format='PNG', optimize=True)
    output.seek(0)

    print(f"  [✓] Outfit image generated!")
    return send_file(output, mimetype='image/png')


@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'api': 'FLASH OUTFIT API',
        'usage': '/outfit?uid=3419823759&key=Flash',
        'status': 'online'
    })


if __name__ == '__main__':
    print("=" * 50)
    print("  FLASH OUTFIT API")
    print("  Port: 5000")
    print(f"  Usage: http://100.88.95.201:5000/outfit?uid=3419823759&key={API_KEYS[0]}")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
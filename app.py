from flask import Flask, request, jsonify, send_file
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor
import os

app = Flask(__name__)
executor = ThreadPoolExecutor(max_workers=10)
session = requests.Session()

# --- Configuration ---
API_KEY = "Flash"
BACKGROUND_FILENAME = "outfit.png"
IMAGE_TIMEOUT = 8
CANVAS_SIZE = (800, 800)
BACKGROUND_MODE = 'cover'

def fetch_player_info(uid: str, region: str):
    if not uid or not region:
        return None
    
    player_info_url = f"https://flash-player-info.vercel.app/info?uid={uid}&key=Flash&region={region}"
    
    try:
        resp = session.get(player_info_url, timeout=IMAGE_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        
        weapon_skins = data.get("basicInfo", {}).get("weaponSkinShows", [])
        
        formatted_data = {
            "AccountInfo": {
                # Basic fields
                "AccountId": data.get("basicInfo", {}).get("accountId"),
                "AccountType": data.get("basicInfo", {}).get("accountType"),
                "Nickname": data.get("basicInfo", {}).get("nickname"),
                "ExternalId": data.get("basicInfo", {}).get("externalId"),
                "Region": data.get("basicInfo", {}).get("region"),
                "Level": data.get("basicInfo", {}).get("level"),
                "Exp": data.get("basicInfo", {}).get("exp"),
                "ExternalType": data.get("basicInfo", {}).get("externalType"),
                "ExternalName": data.get("basicInfo", {}).get("externalName"),
                "ExternalIcon": data.get("basicInfo", {}).get("externalIcon"),
                "BannerId": data.get("basicInfo", {}).get("bannerId"),
                "HeadPic": data.get("basicInfo", {}).get("headPic"),
                "ClanName": data.get("basicInfo", {}).get("clanName"),
                "Rank": data.get("basicInfo", {}).get("rank"),
                "RankingPoints": data.get("basicInfo", {}).get("rankingPoints"),
                "Role": data.get("basicInfo", {}).get("role"),
                "HasElitePass": data.get("basicInfo", {}).get("hasElitePass"),
                "BadgeCnt": data.get("basicInfo", {}).get("badgeCnt"),
                "BadgeId": data.get("basicInfo", {}).get("badgeId"),
                "SeasonId": data.get("basicInfo", {}).get("seasonId"),
                "Liked": data.get("basicInfo", {}).get("liked"),
                "IsDeleted": data.get("basicInfo", {}).get("isDeleted"),
                "ShowRank": data.get("basicInfo", {}).get("showRank"),
                "LastLoginAt": data.get("basicInfo", {}).get("lastLoginAt"),
                "ExternalUid": data.get("basicInfo", {}).get("externalUid"),
                "ReturnAt": data.get("basicInfo", {}).get("returnAt"),
                "ChampionshipTeamName": data.get("basicInfo", {}).get("championshipTeamName"),
                "ChampionshipTeamMemberNum": data.get("basicInfo", {}).get("championshipTeamMemberNum"),
                "ChampionshipTeamId": data.get("basicInfo", {}).get("championshipTeamId"),
                "CsRank": data.get("basicInfo", {}).get("csRank"),
                "CsRankingPoints": data.get("basicInfo", {}).get("csRankingPoints"),
                "WeaponSkinShows": data.get("basicInfo", {}).get("weaponSkinShows", []),
                "PinId": data.get("basicInfo", {}).get("pinId"),
                "IsCsRankingBan": data.get("basicInfo", {}).get("isCsRankingBan"),
                "MaxRank": data.get("basicInfo", {}).get("maxRank"),
                "CsMaxRank": data.get("basicInfo", {}).get("csMaxRank"),
                "MaxRankingPoints": data.get("basicInfo", {}).get("maxRankingPoints"),
                "GameBagShow": data.get("basicInfo", {}).get("gameBagShow"),
                "PeakRankPos": data.get("basicInfo", {}).get("peakRankPos"),
                "CsPeakRankPos": data.get("basicInfo", {}).get("csPeakRankPos"),
                "AccountPrefers": data.get("basicInfo", {}).get("accountPrefers", {}),
                "PeriodicRankingPoints": data.get("basicInfo", {}).get("periodicRankingPoints"),
                "PeriodicRank": data.get("basicInfo", {}).get("periodicRank"),
                "CreateAt": data.get("basicInfo", {}).get("createAt"),
                "VeteranLeaveDaysTag": data.get("basicInfo", {}).get("veteranLeaveDaysTag"),
                "SelectedItemSlots": data.get("basicInfo", {}).get("selectedItemSlots", []),
                "PreVeteranType": data.get("basicInfo", {}).get("preVeteranType"),
                "Title": data.get("basicInfo", {}).get("title"),
                "ExternalIconInfo": data.get("basicInfo", {}).get("externalIconInfo", {}),
                "ReleaseVersion": data.get("basicInfo", {}).get("releaseVersion"),
                "VeteranExpireTime": data.get("basicInfo", {}).get("veteranExpireTime"),
                "ShowBrRank": data.get("basicInfo", {}).get("showBrRank"),
                "ShowCsRank": data.get("basicInfo", {}).get("showCsRank"),
                "ClanId": data.get("basicInfo", {}).get("clanId"),
                "ClanBadgeId": data.get("basicInfo", {}).get("clanBadgeId"),
                "CustomClanBadge": data.get("basicInfo", {}).get("customClanBadge"),
                "UseCustomClanBadge": data.get("basicInfo", {}).get("useCustomClanBadge"),
                "ClanFrameId": data.get("basicInfo", {}).get("clanFrameId"),
                "MembershipState": data.get("basicInfo", {}).get("membershipState"),
                "SelectOccupations": data.get("basicInfo", {}).get("selectOccupations", []),
                "SocialHighLightsWithBasicInfo": data.get("basicInfo", {}).get("socialHighLightsWithBasicInfo", {})
            },
            
            "AccountProfileInfo": {
                # AvatarProfile fields
                "AvatarId": data.get("profileInfo", {}).get("avatarId"),
                "CharacterId": data.get("profileInfo", {}).get("avatarId"),
                "SkinColor": data.get("profileInfo", {}).get("skinColor"),
                "Clothes": data.get("profileInfo", {}).get("clothes", []),
                "EquippedOutfitIds": data.get("profileInfo", {}).get("clothes", []),
                "EquipedSkills": data.get("profileInfo", {}).get("equipedSkills", []),
                "IsSelected": data.get("profileInfo", {}).get("isSelected"),
                "PvePrimaryWeapon": data.get("profileInfo", {}).get("pvePrimaryWeapon"),
                "IsSelectedAwaken": data.get("profileInfo", {}).get("isSelectedAwaken"),
                "EndTime": data.get("profileInfo", {}).get("endTime"),
                "UnlockType": data.get("profileInfo", {}).get("unlockType"),
                "UnlockTime": data.get("profileInfo", {}).get("unlockTime"),
                "IsMarkedStar": data.get("profileInfo", {}).get("isMarkedStar"),
                "ClothesTailorEffects": data.get("profileInfo", {}).get("clothesTailorEffects", [])
            },
            
            "GuildInfo": {
                # ClanInfoBasic fields
                "GuildId": str(data.get("clanBasicInfo", {}).get("clanId")) if data.get("clanBasicInfo", {}).get("clanId") else None,
                "GuildName": data.get("clanBasicInfo", {}).get("clanName"),
                "CaptainId": str(data.get("clanBasicInfo", {}).get("captainId")) if data.get("clanBasicInfo", {}).get("captainId") else None,
                "GuildLevel": data.get("clanBasicInfo", {}).get("clanLevel"),
                "Capacity": data.get("clanBasicInfo", {}).get("capacity"),
                "MemberNum": data.get("clanBasicInfo", {}).get("memberNum"),
                "HonorPoint": data.get("clanBasicInfo", {}).get("honorPoint")
            },
            
            "captainBasicInfo": {
                # AccountInfoBasic for captain
                "AccountId": data.get("captainBasicInfo", {}).get("accountId"),
                "Nickname": data.get("captainBasicInfo", {}).get("nickname"),
                "Level": data.get("captainBasicInfo", {}).get("level"),
                "Region": data.get("captainBasicInfo", {}).get("region"),
                "HeadPic": data.get("captainBasicInfo", {}).get("headPic"),
                "Title": data.get("captainBasicInfo", {}).get("title"),
                "BadgeId": data.get("captainBasicInfo", {}).get("badgeId"),
                "BadgeCnt": data.get("captainBasicInfo", {}).get("badgeCnt"),
                "BannerId": data.get("captainBasicInfo", {}).get("bannerId"),
                "Liked": data.get("captainBasicInfo", {}).get("liked"),
                "Rank": data.get("captainBasicInfo", {}).get("rank"),
                "RankingPoints": data.get("captainBasicInfo", {}).get("rankingPoints"),
                "CsRank": data.get("captainBasicInfo", {}).get("csRank"),
                "CsRankingPoints": data.get("captainBasicInfo", {}).get("csRankingPoints"),
                "MaxRank": data.get("captainBasicInfo", {}).get("maxRank"),
                "CsMaxRank": data.get("captainBasicInfo", {}).get("csMaxRank"),
                "WeaponSkinShows": data.get("captainBasicInfo", {}).get("weaponSkinShows", []),
                "EquippedGuns": data.get("captainBasicInfo", {}).get("weaponSkinShows", []),
                "ReleaseVersion": data.get("captainBasicInfo", {}).get("releaseVersion"),
                "ShowBrRank": data.get("captainBasicInfo", {}).get("showBrRank"),
                "ShowCsRank": data.get("captainBasicInfo", {}).get("showCsRank"),
                "AccountPrefers": data.get("captainBasicInfo", {}).get("accountPrefers", {}),
                "ExternalIconInfo": data.get("captainBasicInfo", {}).get("externalIconInfo", {}),
                "CreateAt": data.get("captainBasicInfo", {}).get("createAt"),
                "LastLoginAt": data.get("captainBasicInfo", {}).get("lastLoginAt"),
                "Exp": data.get("captainBasicInfo", {}).get("exp"),
                "VeteranLeaveDaysTag": data.get("captainBasicInfo", {}).get("veteranLeaveDaysTag"),
                "PreVeteranType": data.get("captainBasicInfo", {}).get("preVeteranType"),
                "VeteranExpireTime": data.get("captainBasicInfo", {}).get("veteranExpireTime"),
                "SocialHighLightsWithBasicInfo": data.get("captainBasicInfo", {}).get("socialHighLightsWithBasicInfo", {})
            },
            
            "creditScoreInfo": {
                # CreditScoreInfoBasic fields
                "CreditScore": data.get("creditScoreInfo", {}).get("creditScore"),
                "IsInit": data.get("creditScoreInfo", {}).get("isInit"),
                "RewardState": data.get("creditScoreInfo", {}).get("rewardState"),
                "PeriodicSummaryLikeCnt": data.get("creditScoreInfo", {}).get("periodicSummaryLikeCnt"),
                "PeriodicSummaryIllegalCnt": data.get("creditScoreInfo", {}).get("periodicSummaryIllegalCnt"),
                "WeeklyMatchCnt": data.get("creditScoreInfo", {}).get("weeklyMatchCnt"),
                "PeriodicSummaryStartTime": data.get("creditScoreInfo", {}).get("periodicSummaryStartTime"),
                "PeriodicSummaryEndTime": data.get("creditScoreInfo", {}).get("periodicSummaryEndTime")
            },
            
            "petInfo": {
                # PetInfo fields
                "Id": data.get("petInfo", {}).get("id"),
                "PetId": data.get("petInfo", {}).get("id"),
                "Name": data.get("petInfo", {}).get("name"),
                "Level": data.get("petInfo", {}).get("level"),
                "Exp": data.get("petInfo", {}).get("exp"),
                "IsSelected": data.get("petInfo", {}).get("isSelected"),
                "SkinId": data.get("petInfo", {}).get("skinId"),
                "Actions": data.get("petInfo", {}).get("actions", []),
                "Skills": data.get("petInfo", {}).get("skills", []),
                "SelectedSkillId": data.get("petInfo", {}).get("selectedSkillId"),
                "IsMarkedStar": data.get("petInfo", {}).get("isMarkedStar"),
                "EndTime": data.get("petInfo", {}).get("endTime")
            },
            
            "socialinfo": {
                # SocialBasicInfo fields
                "AccountId": data.get("socialInfo", {}).get("accountId"),
                "Gender": data.get("socialInfo", {}).get("gender"),
                "Language": data.get("socialInfo", {}).get("language"),
                "TimeOnline": data.get("socialInfo", {}).get("timeOnline"),
                "TimeActive": data.get("socialInfo", {}).get("timeActive"),
                "BattleTag": data.get("socialInfo", {}).get("battleTag", []),
                "SocialTag": data.get("socialInfo", {}).get("socialTag", []),
                "ModePrefer": data.get("socialInfo", {}).get("modePrefer"),
                "Signature": data.get("socialInfo", {}).get("signature"),
                "RankShow": data.get("socialInfo", {}).get("rankShow"),
                "BattleTagCount": data.get("socialInfo", {}).get("battleTagCount", []),
                "SignatureBanExpireTime": data.get("socialInfo", {}).get("signatureBanExpireTime"),
                "LeaderboardTitles": data.get("socialInfo", {}).get("leaderboardTitles", {})
            },
            
            "diamondCostRes": {
                "DiamondCost": data.get("diamondCostRes", {}).get("diamondCost")
            },
            
            # Additional proto fields that might be in the response
            "news": data.get("news", []),
            "historyEpInfo": data.get("historyEpInfo", []),
            "rankingLeaderboardPos": data.get("rankingLeaderboardPos"),
            "equippedAch": data.get("equippedAch", [])
        }
        return formatted_data
    except Exception as e:
        print(f"Error fetching player info: {e}")
        return None

def fetch_and_process_image(image_url: str, size: tuple = None):
    try:
        resp = session.get(image_url, timeout=IMAGE_TIMEOUT)
        resp.raise_for_status()
        img = Image.open(BytesIO(resp.content)).convert("RGBA")
        if size:
            img = img.resize(size, Image.LANCZOS)
        return img
    except Exception:
        return None

# ================== OUTFIT SLOTS CONFIGURATION ==================
OUTFIT_SLOTS = [
    {
        "name": "Head",
        "prefix": "211",
        "default": "211000000",
        "pos": {'x': 355, 'y': 35, 'width': 150, 'height': 150}
    },
    {
        "name": "Face Paint",
        "prefix": "214",
        "default": "214000000",
        "pos": {'x': 575, 'y': 130, 'width': 145, 'height': 145}
    },
    {
        "name": "Mask",
        "prefix": "211",
        "default": "208000000",
        "pos": {'x': 665, 'y': 350, 'width': 150, 'height': 150}
    },
    {
        "name": "Top",
        "prefix": "203",
        "default": "203000000",
        "pos": {'x': 570, 'y': 565, 'width': 150, 'height': 150}
    },
    {
        "name": "Bottom",
        "prefix": "204",
        "default": "204000000",
        "pos": {'x': 355, 'y': 655, 'width': 150, 'height': 150}
    },
    {
        "name": "Shoes",
        "prefix": "205",
        "default": "205000000",
        "pos": {'x': 135, 'y': 565, 'width': 150, 'height': 150}
    },
    {
        "name": "Weapon",
        "prefix": "907",
        "default": "907000000",
        "pos": {'x': 10, 'y': 395, 'width': 210, 'height': 80}
    },
    {
        "name": "Bundle",
        "prefix": "203",
        "default": "212000000",
        "pos": {'x': 135, 'y': 127, 'width': 150, 'height': 150}
    }
]

# ================== INFO ROUTE - JSON DATA ==================
@app.route('/info', methods=['GET'])
def get_info():
    uid = request.args.get('uid')
    region = request.args.get('region')  # Mandatory now
    key = request.args.get('key')

    if key != API_KEY:
        return jsonify({'error': 'Invalid or missing API key'}), 401

    if not uid:
        return jsonify({'error': 'Missing uid parameter'}), 400
    
    if not region:  # Region is mandatory!
        return jsonify({'error': 'Missing region parameter - region is required'}), 400

    player_data = fetch_player_info(uid, region)
    if player_data is None:
        return jsonify({'error': 'Failed to fetch player info'}), 500

    return jsonify(player_data)

# ================== OUTFIT IMAGE ROUTE ==================
@app.route('/outfit', methods=['GET'])
def outfit_image():
    uid = request.args.get('uid')
    region = request.args.get('region')  # Mandatory now
    key = request.args.get('key')

    if key != API_KEY:
        return jsonify({'error': 'Invalid or missing API key'}), 401

    if not uid:
        return jsonify({'error': 'Missing uid parameter'}), 400
    
    if not region:  # Region is mandatory!
        return jsonify({'error': 'Missing region parameter - region is required'}), 400

    player_data = fetch_player_info(uid, region)
    if player_data is None:
        return jsonify({'error': 'Failed to fetch player info'}), 500

    outfit_ids = player_data.get("AccountProfileInfo", {}).get("EquippedOutfitIds", []) or []
    weapon_ids = player_data.get("AccountInfo", {}).get("WeaponSkinShows", []) or []

    used_ids = set()

    def fetch_slot_image(slot):
        # For weapon slot
        if slot["name"] == "Weapon":
            if weapon_ids:
                # Try to find a weapon with 907 prefix first
                for wid in weapon_ids:
                    str_wid = str(wid)
                    if str_wid.startswith("907"):
                        image_url = f'https://iconapi.wasmer.app/{str_wid}'
                        img = fetch_and_process_image(image_url, size=(150, 150))
                        if img:
                            return img
                
                # If no 907 weapon, use first weapon
                if weapon_ids:
                    image_url = f'https://iconapi.wasmer.app/{weapon_ids[0]}'
                    img = fetch_and_process_image(image_url, size=(150, 150))
                    if img:
                        return img
            
            # Default weapon if no weapon_ids
            if slot["default"]:
                image_url = f'https://iconapi.wasmer.app/{slot["default"]}'
                return fetch_and_process_image(image_url, size=(150, 150))
            return None
        
        # For outfit slots
        matched = None
        for oid in outfit_ids:
            try:
                str_oid = str(oid)
            except Exception:
                continue
            if str_oid.startswith(slot["prefix"]) and str_oid not in used_ids:
                matched = str_oid
                used_ids.add(str_oid)
                break
        
        if matched is None and slot["default"]:
            matched = slot["default"]
        
        if matched:
            image_url = f'https://iconapi.wasmer.app/{matched}'
            return fetch_and_process_image(image_url, size=(150, 150))
        return None

    # Load local background image
    bg_path = os.path.join(os.path.dirname(__file__), BACKGROUND_FILENAME)
    try:
        background_image = Image.open(bg_path).convert("RGBA")
    except FileNotFoundError:
        return jsonify({'error': f'Background image not found: {BACKGROUND_FILENAME}. Please add outfit.png file.'}), 500
    except Exception as e:
        return jsonify({'error': f'Failed to open background image: {str(e)}'}), 500

    bg_w, bg_h = background_image.size

    if CANVAS_SIZE is None:
        canvas_w, canvas_h = bg_w, bg_h
        scale_x = scale_y = 1.0
        new_w, new_h = bg_w, bg_h
        background_resized = background_image
        offset_x, offset_y = 0, 0
    else:
        canvas_w, canvas_h = CANVAS_SIZE
        if BACKGROUND_MODE == 'contain':
            scale = min(canvas_w / bg_w, canvas_h / bg_h)
        else:
            scale = max(canvas_w / bg_w, canvas_h / bg_h)
        new_w = max(1, int(bg_w * scale))
        new_h = max(1, int(bg_h * scale))
        background_resized = background_image.resize((new_w, new_h), Image.LANCZOS)

        offset_x = (canvas_w - new_w) // 2
        offset_y = (canvas_h - new_h) // 2
        scale_x = new_w / bg_w
        scale_y = new_h / bg_h

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 255))
    canvas.paste(background_resized, (offset_x, offset_y), background_resized)

    # Fetch and paste all slot images
    for slot in OUTFIT_SLOTS:
        slot_img = fetch_slot_image(slot)
        if not slot_img:
            continue
        
        pos = slot["pos"]
        paste_x = offset_x + int(pos['x'] * scale_x)
        paste_y = offset_y + int(pos['y'] * scale_y)
        paste_w = max(1, int(pos['width'] * scale_x))
        paste_h = max(1, int(pos['height'] * scale_y))

        resized = slot_img.resize((paste_w, paste_h), Image.LANCZOS)
        canvas.paste(resized, (paste_x, paste_y), resized)

    output = BytesIO()
    canvas.save(output, format='PNG')
    output.seek(0)
    return send_file(output, mimetype='image/png')

# ================== DIRECT UID ROUTE ==================
@app.route('/<uid>', methods=['GET'])
def direct_uid(uid):
    # Check if it's an outfit request
    if request.args.get('outfit'):
        return outfit_image()
    
    # For info requests - region mandatory hai
    region = request.args.get('region')
    key = request.args.get('key')
    
    if key != API_KEY:
        return jsonify({'error': 'Invalid or missing API key'}), 401
    
    if not region:  # Region is mandatory!
        return jsonify({'error': 'Missing region parameter - region is required'}), 400
    
    player_data = fetch_player_info(uid, region)
    if player_data is None:
        return jsonify({'error': 'Failed to fetch player info'}), 500
    
    return jsonify(player_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)

#made by juli_dvrma
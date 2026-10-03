import json
import hashlib
import os
import struct
import wave
import zipfile
from pathlib import Path

OUT_FILE = Path('DRAGON_1V1.sb3')
ASSET_DIR = Path('scratch-dragon-1v1/assets')


def ensure_asset_dir():
    ASSET_DIR.mkdir(parents=True, exist_ok=True)


def md5ext_for(path: Path):
    data = path.read_bytes()
    return hashlib.md5(data).hexdigest() + path.suffix


def write_svg(path: Path, body: str):
    svg = f'''<?xml version="1.0" standalone="no"?>
<svg width="480" height="360" viewBox="0 0 480 360" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" x2="0" y1="0" y2="1">
      <stop offset="0%" stop-color="#1d2b4e" />
      <stop offset="100%" stop-color="#090d17" />
    </linearGradient>
  </defs>
  <rect width="480" height="360" fill="url(#bg)"/>
  {body}
</svg>
'''
    path.write_text(svg, encoding='utf-8')


def write_stage_background():
    body = '''
    <rect x="0" y="240" width="480" height="120" fill="#28364c"/>
    <path d="M0 260 L120 215 L170 270 L250 180 L310 250 L420 200 L480 260 L480 360 L0 360 Z" fill="#1a1d2a"/>
    <path d="M20 250 L80 210 L160 250 L120 290 L60 300 Z" fill="#2d3a4d" opacity="0.6"/>
    <path d="M300 245 L360 190 L430 250 L390 295 L330 300 Z" fill="#2d3a4d" opacity="0.6"/>
    <circle cx="395" cy="95" r="35" fill="#efe4b0" opacity="0.25"/>
    <circle cx="90" cy="110" r="26" fill="#8ec5ff" opacity="0.18"/>
  '''
    path = ASSET_DIR / 'arena.svg'
    write_svg(path, body)
    return path


def write_dragon_sprite(path: Path, palette: str, variant: str):
    # palette: fire or ice
    flame = '#ff7b2c' if palette == 'fire' else '#7cd4ff'
    dark = '#7a1d1d' if palette == 'fire' else '#1d3b7a'
    body = f'''
    <g transform="translate(25 20)">
      <ellipse cx="170" cy="255" rx="120" ry="24" fill="rgba(0,0,0,0.32)"/>
      <path d="M68 144 Q100 60 200 60 Q240 60 255 110 L255 180 Q240 228 165 235 L95 235 Q60 222 52 180 Z" fill="{flame}" stroke="#fff" stroke-opacity="0.18"/>
      <path d="M52 177 Q12 122 18 90 Q38 104 48 146 Z" fill="{dark}"/>
      <path d="M242 115 Q270 72 300 88 Q292 120 260 135 Z" fill="{dark}"/>
      <path d="M238 123 L315 85 L330 118 L260 155 Z" fill="{flame}"/>
      <path d="M212 82 L260 40 L292 75 L245 105 Z" fill="{dark}"/>
      <circle cx="248" cy="88" r="8" fill="#1a1720"/>
      <path d="M185 95 L210 120 L195 144 L150 130 Z" fill="#fff" opacity="0.18"/>
      <path d="M115 170 L76 214 L88 240 L142 220 Z" fill="{dark}"/>
      <path d="M180 180 L218 215 L208 245 L158 226 Z" fill="{dark}"/>
      <path d="M140 165 L190 214 L171 250 L118 214 Z" fill="{dark}" opacity="0.88"/>
      <circle cx="104" cy="190" r="5" fill="#ffe1a5" opacity="0.8"/>
      <circle cx="135" cy="190" r="5" fill="#ffe1a5" opacity="0.8"/>
      <path d="M90 112 L120 92 L155 104 L128 130 Z" fill="#ffebbf" opacity="0.18"/>
      <path d="M175 120 L200 104 L220 120 L195 140 Z" fill="#fff" opacity="0.14"/>
    </g>
    '''
    write_svg(path, body)


def write_projectile(path: Path, palette: str):
    if palette == 'fire':
        c1, c2, c3 = '#ffcc66', '#ff7b2c', '#ff3d2e'
    else:
        c1, c2, c3 = '#dff8ff', '#7dd3ff', '#5a8cff'
    body = f'''
    <circle cx="40" cy="40" r="30" fill="{c1}" opacity="0.75"/>
    <circle cx="40" cy="40" r="22" fill="{c2}"/>
    <circle cx="40" cy="40" r="12" fill="{c3}"/>
    <circle cx="53" cy="26" r="8" fill="#fff" opacity="0.5"/>
    '''
    write_svg(path, body)


def write_meteor(path: Path, palette: str):
    body = f'''
    <g>
      <ellipse cx="110" cy="110" rx="85" ry="45" fill="#fdc45b" opacity="0.2"/>
      <path d="M117 23 L134 83 L110 150 L88 82 Z" fill="#ffb347"/>
      <path d="M110 51 L160 92 L110 160 L60 90 Z" fill="#ff6e2e"/>
      <path d="M110 85 L150 110 L110 150 L75 110 Z" fill="#ffd46b" opacity="0.8"/>
      <circle cx="110" cy="88" r="28" fill="#fff1db" opacity="0.8"/>
    </g>
    '''
    write_svg(path, body)


def write_storm(path: Path):
    body = '''
    <g>
      <path d="M50 25 L65 70 L90 70 L70 110 L95 110 L60 190 L52 130 L30 130 L50 25 Z" fill="#d8f4ff"/>
      <path d="M110 35 L130 85 L160 85 L130 135 L165 135 L120 210 L103 155 L75 155 L110 35 Z" fill="#8ad6ff"/>
      <path d="M190 55 L205 95 L225 95 L205 140 L230 140 L190 200 L176 150 L155 150 L190 55 Z" fill="#d9f7ff"/>
    </g>
    '''
    write_svg(path, body)


def write_impact(path: Path, palette: str):
    colors = ('#ffef9c', '#ff7b2c') if palette == 'fire' else ('#e6faff', '#7cd4ff')
    body = f'''
    <g>
      <circle cx="58" cy="58" r="50" fill="{colors[0]}" opacity="0.4"/>
      <circle cx="58" cy="58" r="32" fill="{colors[1]}" opacity="0.75"/>
      <circle cx="58" cy="58" r="14" fill="#fff" opacity="0.8"/>
    </g>
    '''
    write_svg(path, body)


def write_button(path: Path, label: str, accent: str):
    body = f'''
    <rect x="15" y="15" width="170" height="50" rx="10" fill="{accent}"/>
    <text x="100" y="48" text-anchor="middle" font-size="18" font-family="Arial" font-weight="bold" fill="#ffffff">{label}</text>
    '''
    write_svg(path, body)


def generate_sound(path: Path, frequency: float, duration: float, volume: float = 0.2):
    sample_rate = 22050
    total_samples = int(sample_rate * duration)
    frames = []
    import math
    for i in range(total_samples):
        t = i / sample_rate
        if frequency > 0:
            wave_value = math.sin(2 * math.pi * frequency * t)
            envelope = max(0.0, 1.0 - t / duration)
            sample = int(wave_value * envelope * volume * 32767)
        else:
            sample = 0
        frames.append(struct.pack('<h', sample))
    with wave.open(str(path), 'wb') as wavf:
        wavf.setnchannels(1)
        wavf.setsampwidth(2)
        wavf.setframerate(sample_rate)
        wavf.writeframes(b''.join(frames))


def create_assets():
    ensure_asset_dir()
    stage = write_stage_background()
    fire = ASSET_DIR / 'fire_dragon.svg'
    ice = ASSET_DIR / 'ice_dragon.svg'
    write_dragon_sprite(fire, 'fire', 'idle')
    write_dragon_sprite(ice, 'ice', 'idle')

    files = {
        'fireball.svg': lambda p: write_projectile(p, 'fire'),
        'iceball.svg': lambda p: write_projectile(p, 'ice'),
        'meteor.svg': lambda p: write_meteor(p, 'fire'),
        'storm.svg': lambda p: write_storm(p),
        'fire_impact.svg': lambda p: write_impact(p, 'fire'),
        'ice_impact.svg': lambda p: write_impact(p, 'ice'),
        'restart_button.svg': lambda p: write_button(p, 'JUGAR DE NUEVO', '#ffb347'),
        'arena.svg': lambda p: write_svg(p, '''<rect width="480" height="360" fill="#0d1320"/>'''),
    }

    for name, builder in files.items():
        builder(ASSET_DIR / name)

    # Importante: reescribir el fondo real del escenario.
    write_stage_background()

    # sonidos
    sound_dir = ASSET_DIR / 'sounds'
    sound_dir.mkdir(exist_ok=True)
    generate_sound(sound_dir / 'hit.wav', 220, 0.12)
    generate_sound(sound_dir / 'fire.wav', 90, 0.22)
    generate_sound(sound_dir / 'ice.wav', 180, 0.30)
    generate_sound(sound_dir / 'special.wav', 60, 0.45)
    generate_sound(sound_dir / 'win.wav', 330, 0.5)
    generate_sound(sound_dir / 'button.wav', 440, 0.08)


def scratch_asset_entry(path: Path):
    data = path.read_bytes()
    md5 = hashlib.md5(data).hexdigest()
    return {
        'assetId': md5,
        'dataFormat': path.suffix[1:],
        'name': path.name,
        'md5ext': f'{md5}{path.suffix}',
        'size': len(data),
    }


def build_project_json():
    # Stage target
    stage = {
        'isStage': True,
        'name': 'Stage',
        'variables': {
            'vida1': [100, 'vida1'],
            'vida2': [100, 'vida2'],
            'combo1': [0, 'combo1'],
            'combo2': [0, 'combo2'],
            'habilidad1': [0, 'habilidad1'],
            'habilidad2': [0, 'habilidad2'],
            'cooldown1': [0, 'cooldown1'],
            'cooldown2': [0, 'cooldown2'],
        },
        'lists': {},
        'broadcasts': {},
        'blocks': {},
        'comments': {},
        'currentCostume': 0,
        'costumes': [{
            'assetId': hashlib.md5((ASSET_DIR / 'arena.svg').read_bytes()).hexdigest(),
            'name': 'arena',
            'bitmapResolution': 1,
            'dataFormat': 'svg',
            'md5ext': md5ext_for(ASSET_DIR / 'arena.svg'),
            'rotationCenterX': 240,
            'rotationCenterY': 180,
        }],
        'sounds': [],
        'volume': 100,
        'layerOrder': 0,
        'tempoBPM': 60,
        'videoTransparency': 50,
        'videoState': 'on',
        'textToSpeechLanguage': None,
    }

    # Dragon sprite template
    def dragon_sprite(name, costume_name, x_pos, y_pos):
        costume = ASSET_DIR / costume_name
        return {
            'name': name,
            'isStage': False,
            'variables': {},
            'lists': {},
            'broadcasts': {},
            'blocks': {},
            'comments': {},
            'currentCostume': 0,
            'costumes': [{
                'assetId': hashlib.md5(costume.read_bytes()).hexdigest(),
                'name': name,
                'bitmapResolution': 1,
                'dataFormat': 'svg',
                'md5ext': md5ext_for(costume),
                'rotationCenterX': 150,
                'rotationCenterY': 150,
            }],
            'sounds': [],
            'volume': 100,
            'layerOrder': 1,
            'visible': True,
            'x': x_pos,
            'y': y_pos,
            'size': 100,
            'direction': 90,
            'draggable': False,
            'rotationStyle': 'left-right',
        }

    project = {
        'targets': [
            stage,
            dragon_sprite('Dragón fuego', 'fire_dragon.svg', -140, -10),
            dragon_sprite('Dragón hielo', 'ice_dragon.svg', 140, -10),
            {
                'name': 'Bola de fuego',
                'isStage': False,
                'variables': {},
                'lists': {},
                'broadcasts': {},
                'blocks': {},
                'comments': {},
                'currentCostume': 0,
                'costumes': [{
                    'assetId': hashlib.md5((ASSET_DIR / 'fireball.svg').read_bytes()).hexdigest(),
                    'name': 'fireball',
                    'bitmapResolution': 1,
                    'dataFormat': 'svg',
                    'md5ext': md5ext_for(ASSET_DIR / 'fireball.svg'),
                    'rotationCenterX': 40,
                    'rotationCenterY': 40,
                }],
                'sounds': [],
                'volume': 100,
                'layerOrder': 2,
                'visible': True,
                'x': 0,
                'y': 0,
                'size': 100,
                'direction': 90,
                'draggable': False,
                'rotationStyle': 'all around',
            },
            {
                'name': 'Bola de hielo',
                'isStage': False,
                'variables': {},
                'lists': {},
                'broadcasts': {},
                'blocks': {},
                'comments': {},
                'currentCostume': 0,
                'costumes': [{
                    'assetId': hashlib.md5((ASSET_DIR / 'iceball.svg').read_bytes()).hexdigest(),
                    'name': 'iceball',
                    'bitmapResolution': 1,
                    'dataFormat': 'svg',
                    'md5ext': md5ext_for(ASSET_DIR / 'iceball.svg'),
                    'rotationCenterX': 40,
                    'rotationCenterY': 40,
                }],
                'sounds': [],
                'volume': 100,
                'layerOrder': 3,
                'visible': True,
                'x': 0,
                'y': 0,
                'size': 100,
                'direction': 90,
                'draggable': False,
                'rotationStyle': 'all around',
            },
            {
                'name': 'Meteorito infernal',
                'isStage': False,
                'variables': {},
                'lists': {},
                'broadcasts': {},
                'blocks': {},
                'comments': {},
                'currentCostume': 0,
                'costumes': [{
                    'assetId': hashlib.md5((ASSET_DIR / 'meteor.svg').read_bytes()).hexdigest(),
                    'name': 'meteor',
                    'bitmapResolution': 1,
                    'dataFormat': 'svg',
                    'md5ext': md5ext_for(ASSET_DIR / 'meteor.svg'),
                    'rotationCenterX': 110,
                    'rotationCenterY': 110,
                }],
                'sounds': [],
                'volume': 100,
                'layerOrder': 4,
                'visible': True,
                'x': 0,
                'y': 0,
                'size': 100,
                'direction': 90,
                'draggable': False,
                'rotationStyle': 'all around',
            },
            {
                'name': 'Tormenta glacial',
                'isStage': False,
                'variables': {},
                'lists': {},
                'broadcasts': {},
                'blocks': {},
                'comments': {},
                'currentCostume': 0,
                'costumes': [{
                    'assetId': hashlib.md5((ASSET_DIR / 'storm.svg').read_bytes()).hexdigest(),
                    'name': 'storm',
                    'bitmapResolution': 1,
                    'dataFormat': 'svg',
                    'md5ext': md5ext_for(ASSET_DIR / 'storm.svg'),
                    'rotationCenterX': 120,
                    'rotationCenterY': 120,
                }],
                'sounds': [],
                'volume': 100,
                'layerOrder': 5,
                'visible': True,
                'x': 0,
                'y': 0,
                'size': 100,
                'direction': 90,
                'draggable': False,
                'rotationStyle': 'all around',
            },
            {
                'name': 'Botón reinicio',
                'isStage': False,
                'variables': {},
                'lists': {},
                'broadcasts': {},
                'blocks': {},
                'comments': {},
                'currentCostume': 0,
                'costumes': [{
                    'assetId': hashlib.md5((ASSET_DIR / 'restart_button.svg').read_bytes()).hexdigest(),
                    'name': 'restart',
                    'bitmapResolution': 1,
                    'dataFormat': 'svg',
                    'md5ext': md5ext_for(ASSET_DIR / 'restart_button.svg'),
                    'rotationCenterX': 100,
                    'rotationCenterY': 35,
                }],
                'sounds': [],
                'volume': 100,
                'layerOrder': 6,
                'visible': True,
                'x': 0,
                'y': -150,
                'size': 100,
                'direction': 90,
                'draggable': False,
                'rotationStyle': 'all around',
            },
        ],
        'monitors': [],
        'extensions': [],
        'meta': {
            'semver': '3.0.0',
            'vm': '0.2.0',
            'agent': 'dragonscratch-script',
            'version': '1.0.0'
        },
        'info': {
            'projectID': 'dragon-1v1',
            'user': 'scratch-export',
            'author': 'GitHub Copilot'
        }
    }
    return project


def build_sb3():
    create_assets()
    project_json = build_project_json()

    out = OUT_FILE
    out.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(out, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr('project.json', json.dumps(project_json, separators=(',', ':')))
        for path in ASSET_DIR.rglob('*'):
            if path.is_file() and path.name != 'README.md':
                zf.write(path, arcname=f'assets/{path.name}')

    print(f'Archivo generado: {out.resolve()}')
    print('Abre ese archivo en Scratch 3.0.')


if __name__ == '__main__':
    build_sb3()

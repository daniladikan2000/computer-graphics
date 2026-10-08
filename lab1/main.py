from flask import Flask, render_template, request, jsonify
from dataclasses import asdict
from models import RGB, CMYK, HSV
from processing import rgb_to_cmyk, cmyk_to_rgb, rgb_to_hsv, hsv_to_rgb, rgb_to_hex, hex_to_rgb
from errors import ColorError

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/convert', methods=['POST'])
def convert():
    data = request.json
    source = data.get('source')
    val = data.get('values')

    try:
        if source == 'rgb': 
            rgb = RGB(int(val['r']), int(val['g']), int(val['b']))
        elif source == 'cmyk': 
            rgb = cmyk_to_rgb(CMYK(int(val['c']), int(val['m']), int(val['y']), int(val['k'])))
        elif source == 'hsv': 
            rgb = hsv_to_rgb(HSV(int(val['h']), int(val['s']), int(val['v'])))
        elif source == 'hex': 
            rgb = hex_to_rgb(val['hex'])
        else: 
            return jsonify({'error': 'Неизвестный источник'}), 400

        return jsonify({
            'rgb': asdict(rgb),
            'cmyk': asdict(rgb_to_cmyk(rgb)),
            'hsv': asdict(rgb_to_hsv(rgb)),
            'hex': rgb_to_hex(rgb)
        })
    except (ColorError, ValueError) as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
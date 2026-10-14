from flask import Flask, jsonify, render_template_string, abort
import random

app = Flask(__name__)

# LIST: daftar kata untuk setiap level
LEVELS = {
    "mudah": ["kucing", "rumah", "buku", "meja", "bola", "air", "api", "nasi", "sapu", "topi"],
    "sedang": ["komputer", "sekolah", "bermain", "keyboard", "internet", "belajar", "program", "jendela", "pelangi", "tanaman"],
    "sulit": ["pengetahuan", "kebahagiaan", "kemerdekaan", "perpustakaan", "telekomunikasi", "keanekaragaman", "penyelenggaraan", "pertanggungjawaban"],
}

# LOOP: membuat daftar info level (dipakai untuk tombol menu)
LEVEL_INFO = []
for nama, daftar_kata in LEVELS.items():
    LEVEL_INFO.append({"nama": nama, "jumlah": len(daftar_kata)})

JUMLAH_KATA_PER_GAME = 6

HTML = """
<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Game Mengetik</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f0f4ff; display: flex;
           justify-content: center; padding: 30px 15px; margin: 0; }
    .kotak { background: white; max-width: 420px; width: 100%; padding: 28px;
             border-radius: 16px; box-shadow: 0 4px 16px rgba(0,0,0,.1); text-align: center; }
    h1 { margin-top: 0; color: #2b3a67; }
    button { display: block; width: 100%; padding: 14px; margin: 10px 0; font-size: 17px;
             border: none; border-radius: 10px; background: #4c6ef5; color: white; cursor: pointer; }
    button:hover { background: #3b5bdb; }
    button.abu { background: #868e96; }
    .hidden { display: none; }
    .kata { font-size: 36px; font-weight: bold; letter-spacing: 2px; margin: 20px 0; color: #2b3a67; }
    input { width: 100%; box-sizing: border-box; padding: 12px; font-size: 20px;
            border: 2px solid #ced4da; border-radius: 10px; text-align: center; }
    input.salah { border-color: #e03131; background: #fff5f5; }
    .info { color: #555; }
  </style>
</head>
<body>
<div class="kotak">

  <!-- MENU UTAMA -->
  <div id="menu" class="layar">
    <h1>⌨️ Game Mengetik</h1>
    <p class="info">Ketik kata secepat mungkin!</p>
    <button onclick="tampil('pilih')">▶ Mulai Main</button>
    <button onclick="tampil('cara')">❓ Cara Main</button>
  </div>

  <!-- PILIH LEVEL -->
  <div id="pilih" class="layar hidden">
    <h1>Pilih Level</h1>
    {% for lv in levels %}
      <button onclick="mulaiGame('{{ lv.nama }}')">{{ lv.nama.capitalize() }} ({{ lv.jumlah }} kata tersedia)</button>
    {% endfor %}
    <button class="abu" onclick="tampil('menu')">← Kembali</button>
  </div>

  <!-- CARA MAIN -->
  <div id="cara" class="layar hidden">
    <h1>Cara Main</h1>
    <p>1. Pilih level.<br>2. Ketik kata yang muncul dengan benar.<br>
       3. Kata berikutnya muncul otomatis.<br>4. Selesaikan semua kata secepat mungkin!</p>
    <button class="abu" onclick="tampil('menu')">← Kembali</button>
  </div>

  <!-- GAME -->
  <div id="game" class="layar hidden">
    <p class="info">Kata <span id="nomor">1</span>/<span id="total">0</span> • Waktu: <span id="waktu">0.0</span>s</p>
    <div class="kata" id="kata"></div>
    <input id="input" autocomplete="off" autocapitalize="off" spellcheck="false" placeholder="Ketik di sini...">
    <button class="abu" onclick="batal()">Menyerah</button>
  </div>

  <!-- HASIL -->
  <div id="hasil" class="layar hidden">
    <h1>🎉 Selesai!</h1>
    <p id="teks-hasil" class="info"></p>
    <button onclick="tampil('pilih')">Main Lagi</button>
    <button class="abu" onclick="tampil('menu')">Menu Utama</button>
  </div>

</div>

<script>
  let daftarKata = [], indeks = 0, waktuMulai = 0, timer = null;
  const input = document.getElementById('input');

  function tampil(id) {
    document.querySelectorAll('.layar').forEach(el => el.classList.add('hidden'));
    document.getElementById(id).classList.remove('hidden');
  }

  async function mulaiGame(level) {
    const res = await fetch('/api/kata/' + level);
    daftarKata = await res.json();
    indeks = 0;
    document.getElementById('total').textContent = daftarKata.length;
    tampilKata();
    tampil('game');
    input.value = '';
    input.focus();
    waktuMulai = Date.now();
    clearInterval(timer);
    timer = setInterval(() => {
      document.getElementById('waktu').textContent = ((Date.now() - waktuMulai) / 1000).toFixed(1);
    }, 100);
  }

  function tampilKata() {
    document.getElementById('kata').textContent = daftarKata[indeks];
    document.getElementById('nomor').textContent = indeks + 1;
  }

  input.addEventListener('input', () => {
    const target = daftarKata[indeks];
    const ketikan = input.value.trim().toLowerCase();
    input.classList.toggle('salah', !target.startsWith(ketikan));
    if (ketikan === target) {
      indeks++;
      input.value = '';
      if (indeks >= daftarKata.length) { selesai(); } else { tampilKata(); }
    }
  });

  function selesai() {
    clearInterval(timer);
    const detik = (Date.now() - waktuMulai) / 1000;
    const kpm = Math.round(daftarKata.length / (detik / 60));
    document.getElementById('teks-hasil').textContent =
      'Waktu: ' + detik.toFixed(1) + ' detik • Kecepatan: ' + kpm + ' kata/menit';
    tampil('hasil');
  }

  function batal() { clearInterval(timer); tampil('menu'); }
</script>
</body>
</html>
"""


@app.route("/")
def index():
    return render_template_string(HTML, levels=LEVEL_INFO)


@app.route("/api/kata/<level>")
def ambil_kata(level):
    if level not in LEVELS:
        abort(404)
    # Ambil beberapa kata acak dari list level yang dipilih
    return jsonify(random.sample(LEVELS[level], JUMLAH_KATA_PER_GAME))


if __name__ == "__main__":
    app.run(debug=True)

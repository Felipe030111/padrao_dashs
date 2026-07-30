# -*- coding: utf-8 -*-
"""
Padrão de DRILL — clique numa linha/número e abra um modal com o detalhe,
com botão "Exportar Excel".

Como funciona:
  - Cada linha da tabela principal recebe data-drill="<chave>" (ex.: a obra).
  - Um objeto JS DRILL_DATA[chave] = {"title":..., "headers":[...], "rows":[[...]]}
    é embutido na página (JSON) OU o modal chama uma rota que devolve o detalhe.
  - O botão "Exportar Excel" aponta para /export/<chave>.xlsx (ver export_excel.py).

Montagem na página:
    from drill import DRILL_CSS, drill_modal_html, drill_js
    import json
    ...<style> {DRILL_CSS} </style>
    ...<tabela com <tr data-drill="114">...>
    {drill_modal_html(export_base="/export")}
    <script>var DRILL_DATA = {json.dumps(dados)};</script>
    <script>{drill_js(export_base="/export")}</script>

Onde `dados = {"114": {"title":"Obra #114","headers":["Conta","Real","Comp"],
                      "rows":[["Mão de obra",1000,1200], ...]}}`.
"""
import json


def drill_modal_html(export_base="/export"):
    return """
<div class="ov" id="drillOv"><div class="dmodal">
  <div class="dhead">
    <div><h3 id="dTitle">Detalhe</h3></div>
    <div class="dhead-actions">
      <a id="dExport" class="dbtn" href="#">⬇ Exportar Excel</a>
      <button class="dx" id="dClose">&times;</button>
    </div>
  </div>
  <div class="dbody"><table class="dt"><thead id="dThead"></thead><tbody id="dTbody"></tbody></table></div>
</div></div>
"""


def drill_js(export_base="/export"):
    return """
(function(){
  var ov=document.getElementById('drillOv');
  function close(){ ov.classList.remove('open'); }
  function open(key){
    var d=(window.DRILL_DATA||{})[key]; if(!d) return;
    document.getElementById('dTitle').textContent=d.title||'Detalhe';
    var th=d.headers.map(function(h){return '<th>'+h+'</th>';}).join('');
    document.getElementById('dThead').innerHTML='<tr>'+th+'</tr>';
    document.getElementById('dTbody').innerHTML=(d.rows||[]).map(function(r){
      return '<tr>'+r.map(function(c){return '<td>'+c+'</td>';}).join('')+'</tr>';
    }).join('');
    document.getElementById('dExport').href='%EXPORT%/'+encodeURIComponent(key)+'.xlsx';
    ov.classList.add('open');
  }
  document.getElementById('dClose').onclick=close;
  ov.addEventListener('click',function(e){ if(e.target===ov) close(); });
  document.querySelectorAll('[data-drill]').forEach(function(el){
    el.style.cursor='pointer';
    el.addEventListener('click',function(){ open(el.getAttribute('data-drill')); });
  });
  window.openDrill=open;
})();
""".replace("%EXPORT%", export_base)


DRILL_CSS = """
.ov{position:fixed;inset:0;background:rgba(20,25,32,.55);display:none;align-items:center;justify-content:center;z-index:50}
.ov.open{display:flex}
.dmodal{background:#fff;width:820px;max-width:94vw;max-height:86vh;border-radius:16px;box-shadow:0 24px 70px rgba(0,0,0,.4);display:flex;flex-direction:column;overflow:hidden}
.dhead{display:flex;justify-content:space-between;align-items:center;gap:12px;padding:16px 20px;border-bottom:1px solid #eef0f2}
.dhead h3{font-size:15px;font-weight:800;color:#0b3d24}
.dhead-actions{display:flex;align-items:center;gap:10px}
.dbtn{background:linear-gradient(145deg,#0a7a48,#005330);color:#fff;text-decoration:none;border-radius:9px;padding:8px 13px;font-size:12px;font-weight:800}
.dbtn:hover{filter:brightness(1.08)}
.dx{border:none;background:#f2f4f6;color:#59616c;width:30px;height:30px;border-radius:9px;font-size:16px;cursor:pointer}
.dbody{overflow:auto;padding:8px 20px 20px}
table.dt{width:100%;border-collapse:collapse;font-size:12px;white-space:nowrap}
table.dt th{position:sticky;top:0;background:#fff;text-align:left;color:#7a828e;font-size:10px;text-transform:uppercase;padding:8px 6px;border-bottom:1px solid #eef0f2}
table.dt td{padding:7px 6px;border-bottom:1px solid #f4f5f6}
table.dt td:not(:first-child){text-align:right;font-variant-numeric:tabular-nums}
"""

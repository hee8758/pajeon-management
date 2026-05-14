import re

src = open('KBS_보도영상국_파견인력관리시스템.html', encoding='utf-8').read()

# Extract parts
script_start = src.find('<script>')
script_end   = src.find('</script>', script_start) + 9
js_block     = src[script_start:script_end]

body_start   = src.find('<body>') + 6
body_html    = src[body_start:script_start]   # app div + modals before script
after_html   = src[script_end:].strip()       # modals after script + </body></html>

NEW_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{
  --bg:#f0f2f7;--surface:#ffffff;--surface2:#f4f6fb;--border:#dde2ee;
  --accent:#4f46e5;--accent2:#e11d7a;--green:#16a34a;--amber:#d97706;
  --red:#dc2626;--blue:#2563eb;--purple:#7c3aed;
  --text:#1e2340;--text2:#4a5272;--text3:#7b85a8;
  --card-bg:#ffffff;--input-bg:#f8f9fd;
}
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Noto Sans KR',sans-serif;font-size:14px;color:var(--text);background:var(--bg);min-height:100vh}
body::before{content:'';position:fixed;inset:0;background:linear-gradient(135deg,#eef1ff 0%,#f5f7ff 40%,#fdf4ff 100%);z-index:-1;}

/* APP SHELL */
.app{max-width:1400px;margin:0 auto;padding:0 1.5rem 2rem}

/* HEADER */
.app-header{
  display:flex;align-items:center;gap:16px;
  padding:1.2rem 0;margin-bottom:1.5rem;
  border-bottom:1px solid var(--border);
  position:sticky;top:0;z-index:50;
  background:rgba(240,242,247,.92);backdrop-filter:blur(12px);
}
.app-header h1{
  font-size:17px;font-weight:700;letter-spacing:-.3px;
  background:linear-gradient(135deg,#4f46e5,#a21caf);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.app-header .subtitle{font-size:11px;color:var(--text3);margin-left:auto}

/* TABS */
.tabs{display:flex;gap:4px;margin-bottom:1.5rem;padding:4px;
  background:rgba(255,255,255,.8);border-radius:14px;width:fit-content;
  box-shadow:0 2px 8px rgba(79,70,229,.08);border:1px solid var(--border)}
.tab{padding:8px 20px;font-size:13px;cursor:pointer;border:none;background:none;
  color:var(--text3);border-radius:10px;font-weight:500;transition:all .2s;font-family:inherit}
.tab:hover{color:var(--accent);background:rgba(79,70,229,.06)}
.tab.active{background:var(--accent);color:#fff;font-weight:600;
  box-shadow:0 4px 14px rgba(79,70,229,.3)}

/* DEPT TABS */
.dept-tabs{display:flex;gap:8px;margin-bottom:1.2rem;flex-wrap:wrap}
.dept-tab{padding:6px 16px;font-size:12px;font-weight:500;border-radius:20px;
  border:1.5px solid var(--border);background:transparent;color:var(--text3);
  cursor:pointer;transition:all .2s}
.dept-tab:hover{border-color:var(--accent);color:var(--accent)}
.dept-tab.active{color:#fff;border-color:transparent;font-weight:600}
.dept-tab:not([class*='d']).active{background:var(--accent)}
.dept-tab.d1.active{background:linear-gradient(135deg,#6c63ff,#4f46e5)}
.dept-tab.d2.active{background:linear-gradient(135deg,#a855f7,#7c3aed)}
.dept-tab.d3.active{background:linear-gradient(135deg,#3b82f6,#2563eb)}

/* SUMMARY CARDS */
.summary{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;margin-bottom:1.5rem}
.scard{background:#fff;border-radius:14px;padding:16px 18px;
  border:1px solid var(--border);transition:all .2s;
  box-shadow:0 2px 8px rgba(79,70,229,.06)}
.scard:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(79,70,229,.12)}
.scard .lbl{font-size:11px;color:var(--text3);margin-bottom:8px;font-weight:500}
.scard .val{font-size:26px;font-weight:700}
.val-blue{color:var(--blue)}.val-green{color:var(--green)}
.val-amber{color:var(--amber)}.val-purple{color:var(--purple)}

/* SEC HEADER */
.sec-header{display:flex;justify-content:space-between;align-items:center;
  margin-bottom:1rem;flex-wrap:wrap;gap:8px}
.sec-header h2{font-size:15px;font-weight:600;color:var(--text)}
.header-btns{display:flex;gap:8px;flex-wrap:wrap}

/* BUTTONS */
.btn{padding:8px 14px;font-size:12px;border-radius:9px;cursor:pointer;
  font-weight:500;border:none;font-family:inherit;transition:all .15s}
.btn-primary{background:var(--accent);color:#fff}
.btn-primary:hover{background:#5a52e0;box-shadow:0 4px 14px rgba(108,99,255,.4)}
.btn-export{background:rgba(34,197,94,.12);color:var(--green);border:1px solid rgba(34,197,94,.25)}
.btn-export:hover{background:rgba(34,197,94,.2)}
.btn-import{background:rgba(59,130,246,.12);color:var(--blue);border:1px solid rgba(59,130,246,.25)}
.btn-import:hover{background:rgba(59,130,246,.2)}
.btn-template{background:var(--surface2);color:var(--text2);border:1px solid var(--border)}
.btn-template:hover{background:var(--surface)}
.btn-outline{background:transparent;color:var(--text2);border:1px solid var(--border)}
.btn-outline:hover{background:var(--surface2)}
.btn-danger{background:transparent;color:var(--red);border:1px solid rgba(239,68,68,.3)}
.btn-danger:hover{background:rgba(239,68,68,.1)}
.btn-cancel{background:none;color:var(--text2);border:1px solid var(--border);
  padding:9px 20px;font-size:13px;border-radius:9px;cursor:pointer;font-family:inherit}
.btn-save{background:var(--accent);color:#fff;border:none;
  padding:9px 24px;font-size:13px;border-radius:9px;cursor:pointer;font-weight:600;font-family:inherit}
.btn-save:hover{background:#5a52e0}

/* FILTER ROW */
.filter-row{display:flex;gap:8px;margin-bottom:1rem;flex-wrap:wrap;align-items:center}
.filter-row select,.filter-row input{
  padding:7px 11px;border:1px solid var(--border);border-radius:9px;
  font-size:12px;background:var(--input-bg);color:var(--text);height:36px;font-family:inherit}
.filter-row input[type=text]{width:150px}
.filter-row input:focus,.filter-row select:focus{outline:none;border-color:var(--accent)}

/* TABLE */
.tbl-wrap{overflow-x:auto;border-radius:14px;border:1px solid var(--border);background:#fff;
  box-shadow:0 2px 12px rgba(79,70,229,.06)}
table{width:100%;border-collapse:collapse;font-size:12px;min-width:1160px}
th{text-align:left;padding:10px 12px;font-weight:600;font-size:11px;color:var(--text3);
  border-bottom:1px solid var(--border);white-space:nowrap;background:#f8f9fd;
  text-transform:uppercase;letter-spacing:.3px}
td{padding:10px 12px;border-bottom:1px solid #eef0f7;vertical-align:middle;white-space:nowrap;color:var(--text)}
tr:last-child td{border-bottom:none}
tr:hover td{background:#f5f6ff}

/* BADGES */
.badge{display:inline-block;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:500}
.b-ing{background:rgba(59,130,246,.15);color:var(--blue)}
.b-end{background:rgba(239,68,68,.15);color:var(--red)}
.b-soon{background:rgba(245,158,11,.15);color:var(--amber)}
.b-ga{background:rgba(59,130,246,.15);color:var(--blue)}
.b-na{background:rgba(245,158,11,.15);color:var(--amber)}
.b-daily{background:rgba(168,85,247,.15);color:var(--purple)}
.b-special{background:rgba(245,158,11,.15);color:var(--amber)}
.b-sports{background:rgba(34,197,94,.15);color:var(--green)}
.b-ingest{background:rgba(59,130,246,.15);color:var(--blue)}
.note-badge{font-size:10px;padding:1px 6px;border-radius:3px;
  background:rgba(245,158,11,.15);color:var(--amber);margin-left:4px}

/* PAGINATION */
.pagination{display:flex;align-items:center;gap:8px;margin-top:1rem;
  justify-content:flex-end;font-size:12px;color:var(--text3)}
.pg-btn{padding:5px 12px;border:1px solid var(--border);border-radius:7px;
  cursor:pointer;background:var(--surface2);color:var(--text2);font-size:12px}
.pg-btn:disabled{opacity:.3;cursor:not-allowed}

/* MODAL */
.modal-bg{position:fixed;inset:0;background:rgba(79,70,229,.15);display:flex;
  align-items:flex-start;justify-content:center;padding-top:40px;z-index:100;overflow-y:auto;
  backdrop-filter:blur(8px)}
.modal{background:#fff;border-radius:18px;border:1px solid var(--border);
  padding:1.75rem;width:100%;max-width:580px;margin-bottom:40px;
  box-shadow:0 24px 64px rgba(79,70,229,.18)}
.modal h3{font-size:17px;font-weight:700;margin-bottom:1.2rem;color:var(--text)}
.modal-footer{display:flex;gap:8px;justify-content:flex-end;
  margin-top:1.2rem;padding-top:1rem;border-top:1px solid var(--border)}

/* FORM */
.form-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.form-grid.three{grid-template-columns:1fr 1fr 1fr}
.fg{display:flex;flex-direction:column;gap:5px}
.fg label{font-size:11px;color:var(--text2);font-weight:600}
.fg input,.fg select,.fg textarea{
  padding:9px 11px;border:1.5px solid var(--border);border-radius:9px;
  font-size:13px;background:#fff;color:var(--text);width:100%;font-family:inherit}
.fg input:focus,.fg select:focus{outline:none;border-color:var(--accent);box-shadow:0 0 0 3px rgba(79,70,229,.1)}
.fg.full{grid-column:1/-1}
.sec-div{font-size:11px;font-weight:600;color:var(--text3);padding-bottom:5px;
  border-bottom:1px solid var(--border);grid-column:1/-1;margin-top:6px;
  text-transform:uppercase;letter-spacing:.5px}

/* SUBTYPE */
.subtype-box{background:var(--surface2);border-radius:9px;padding:10px 14px;
  border:1px solid var(--border);grid-column:1/-1;display:none}
.subtype-box.show{display:block}
.sb-label{font-size:11px;color:var(--text3);font-weight:500;margin-bottom:8px}
.subtype-btns{display:flex;gap:8px}
.st-btn{padding:6px 18px;font-size:12px;border:1px solid var(--border);border-radius:8px;
  cursor:pointer;background:var(--input-bg);color:var(--text3);transition:all .1s;font-family:inherit}
.st-btn.sel-daily{background:rgba(168,85,247,.2);color:var(--purple);border-color:var(--purple);font-weight:500}
.st-btn.sel-special{background:rgba(245,158,11,.2);color:var(--amber);border-color:var(--amber);font-weight:500}
.st-btn.sel-sports{background:rgba(34,197,94,.2);color:var(--green);border-color:var(--green);font-weight:500}

/* UPLOAD ZONE */
.upload-zone{border:2px dashed var(--border);border-radius:12px;padding:16px;
  margin-bottom:12px;display:flex;align-items:center;gap:12px;cursor:pointer;
  background:var(--input-bg);transition:all .15s}
.upload-zone:hover{border-color:var(--accent);background:rgba(108,99,255,.08)}
.upload-zone.dragging{border-color:var(--accent);background:rgba(108,99,255,.1)}
.u-icon{width:40px;height:40px;border-radius:9px;background:rgba(108,99,255,.15);
  display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0}
.u-title{font-size:13px;font-weight:500;color:var(--text)}
.u-sub{font-size:11px;color:var(--text3);margin-top:2px}
.method-tabs{display:flex;gap:6px;margin-bottom:12px}
.m-tab{padding:5px 14px;font-size:12px;border:1px solid var(--border);border-radius:7px;
  cursor:pointer;background:var(--surface2);color:var(--text3);font-family:inherit}
.m-tab.active{background:var(--accent);color:#fff;border-color:var(--accent)}
.paste-area{width:100%;height:90px;padding:9px 11px;border:1px solid var(--border);
  border-radius:9px;font-size:12px;resize:vertical;font-family:inherit;
  color:var(--text);background:var(--input-bg)}
.btn-parse-text{margin-top:8px;padding:8px 18px;background:var(--blue);color:#fff;
  border:none;border-radius:9px;font-size:12px;cursor:pointer;font-weight:500;font-family:inherit}

/* AI STATUS */
.ai-status{display:none;align-items:center;gap:8px;font-size:12px;
  padding:9px 12px;border-radius:9px;margin-bottom:10px}
.ai-status.show{display:flex}
.ai-status.loading{background:rgba(59,130,246,.12);color:var(--blue)}
.ai-status.done{background:rgba(34,197,94,.12);color:var(--green)}
.ai-status.err{background:rgba(239,68,68,.12);color:var(--red)}
.spinner{width:13px;height:13px;border:2px solid rgba(255,255,255,.15);
  border-top:2px solid var(--blue);border-radius:50%;
  animation:spin .8s linear infinite;flex-shrink:0}
@keyframes spin{to{transform:rotate(360deg)}}
.filled-badge{display:inline-block;padding:1px 5px;background:rgba(34,197,94,.15);
  color:var(--green);border-radius:3px;font-size:10px;margin-left:4px;vertical-align:middle}

/* AI RESULT */
.ai-result{display:none;background:rgba(34,197,94,.06);border:1px solid rgba(34,197,94,.2);
  border-radius:9px;padding:12px;margin-bottom:12px}
.ai-result.show{display:block}
.ai-result-title{font-size:11px;font-weight:600;color:var(--green);margin-bottom:8px}
.ai-result-grid{display:grid;grid-template-columns:1fr 1fr;gap:3px 16px}
.ai-result-row{font-size:12px;display:flex;gap:6px}
.ai-result-key{color:var(--text3);min-width:54px;flex-shrink:0}
.ai-result-val{color:var(--text);font-weight:500}

/* AGENCY GRID */
.agency-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-top:1rem}
.agency-card{background:var(--card-bg);border:1px solid var(--border);border-radius:14px;
  padding:18px 20px;transition:all .2s}
.agency-card:hover{box-shadow:0 8px 24px rgba(0,0,0,.3);transform:translateY(-2px)}
.agency-name{font-size:15px;font-weight:700;color:var(--text)}
.agency-info{font-size:12px;color:var(--text3);margin-top:3px}
.agency-status{font-size:11px;padding:3px 10px;border-radius:5px;
  background:var(--surface2);color:var(--text3)}
.agency-status.on{background:rgba(34,197,94,.15);color:var(--green)}

/* HISTORY */
.hist-item{padding:12px 0;border-bottom:1px solid var(--border);display:flex;gap:12px;align-items:flex-start}
.hist-item:last-child{border-bottom:none}
.hdot{width:8px;height:8px;border-radius:50%;margin-top:5px;flex-shrink:0}
.hdot.new{background:var(--blue)}.hdot.replace{background:var(--amber)}
.hist-date{font-size:11px;color:var(--text3);margin-top:2px}

/* EXCEL IMPORT */
.excel-drop{border:2px dashed rgba(34,197,94,.3);border-radius:12px;padding:24px;
  text-align:center;background:rgba(34,197,94,.05);cursor:pointer;margin-bottom:1rem}
.excel-drop:hover{border-color:var(--green);background:rgba(34,197,94,.08)}
.col-map{display:grid;grid-template-columns:1fr 1fr;gap:8px;max-height:240px;overflow-y:auto;margin-bottom:1rem}
.col-row{display:flex;flex-direction:column;gap:4px}
.col-row label{font-size:11px;color:var(--text3)}
.col-row select{padding:5px 8px;border:1px solid var(--border);border-radius:7px;
  font-size:12px;background:var(--input-bg);color:var(--text)}
.import-info{font-size:12px;padding:9px 12px;background:var(--surface2);
  border-radius:9px;margin-bottom:12px;color:var(--text2)}

/* EMPTY */
.empty{text-align:center;padding:3rem;color:var(--text3);font-size:13px}

/* FORMAT BADGES */
.fmt-kbs{background:rgba(239,68,68,.15);color:var(--red);border:1px solid rgba(239,68,68,.2)}
.fmt-mi{background:rgba(59,130,246,.15);color:var(--blue);border:1px solid rgba(59,130,246,.2)}
.fmt-primus{background:rgba(34,197,94,.15);color:var(--green);border:1px solid rgba(34,197,94,.2)}
.fmt-etc{background:var(--surface2);color:var(--text3);border:1px solid var(--border)}
.fmt-badge{padding:3px 8px;border-radius:4px;font-size:10px;font-weight:500}

/* PAGE SWITCH */
.page{display:none}.page.active{display:block;animation:fadeIn .2s ease}
@keyframes fadeIn{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}

/* WAGE TABLE */
#wage-panel{background:#fff;border:1px solid var(--border);border-radius:14px;
  padding:1.25rem;margin-bottom:1.2rem;box-shadow:0 2px 8px rgba(79,70,229,.06)}
#wage-panel input{background:#f8f9fd;color:var(--text);border:1px solid var(--border);
  border-radius:7px;padding:5px 8px;font-size:13px}

/* DAY EDIT OVERLAY */
#day-edit-overlay{background:rgba(79,70,229,.12);backdrop-filter:blur(10px)}
#day-edit-overlay > div{background:#fff;border:1px solid var(--border);border-radius:18px;
  box-shadow:0 24px 64px rgba(79,70,229,.18)}
#dem-start,#dem-end{background:#f8f9fd!important;color:var(--text)!important;
  border:2px solid var(--border)!important;border-radius:10px!important}

/* SCROLLBAR */
::-webkit-scrollbar{width:5px;height:5px}
::-webkit-scrollbar-track{background:#eef0f7}
::-webkit-scrollbar-thumb{background:#c5cae0;border-radius:3px}

/* SELECT & INPUT GLOBAL */
select,input,textarea{color-scheme:light}


/* ══════════════════════════════════
   파견료 정산 탭 — 라이트 테마 보정
   원본 JS의 흰 배경/연한 색상 인라인 스타일을
   라이트 테마에 맞게 보정
   ══════════════════════════════════ */

/* 요약 카드 */
#pay-content > div[style*="background:#f5f5f3"] { background:#f4f6fb!important; }
#pay-content > div[style*="background:#FFF3E8"] { background:#fffbf0!important; border:1px solid #fde68a!important; }
#pay-content > div[style*="background:#E6F1FB"] { background:#eff6ff!important; border:1px solid #bfdbfe!important; }

/* 정산 목록 테이블 */
#pay-content table { background:#fff; }
#pay-content thead tr { background:#f8f9fd!important; }
#pay-content thead th { color:#7b85a8!important; border-bottom:1px solid #dde2ee!important; }
#pay-content tbody tr:hover td { background:#f5f6ff!important; }
#pay-content tbody td { color:#1e2340!important; border-bottom:1px solid #eef0f7!important; }

/* 성명 컬럼 */
#pay-content td[style*="font-weight:500"] { color:#1e2340!important; font-weight:600!important; }

/* 기본급 숫자 */
#pay-content td[style*="text-align:right"][style*="color:#888"] { color:#4a5272!important; font-weight:500!important; }

/* 시간외수당 — 주황 */
#pay-content td[style*="color:#854F0B"] { color:#b45309!important; font-weight:600!important; }
#pay-content td[style*="color:#ccc"] { color:#c5cae0!important; }

/* 총 파견료 — 파랑 */
#pay-content td[style*="color:#185FA5"] { color:#1d4ed8!important; font-weight:700!important; }

/* 직군 배지 */
#pay-content span[style*="background:#E6F1FB"] { background:#dbeafe!important; color:#1d4ed8!important; }
#pay-content span[style*="background:#EEEDFE"] { background:#ede9fe!important; color:#5b21b6!important; }
#pay-content span[style*="background:#FAEEDA"] { background:#fef3c7!important; color:#92400e!important; }
#pay-content span[style*="background:#FCEBEB"] { background:#fee2e2!important; color:#991b1b!important; }

/* 버튼 */
#pay-content span[style*="background:#f5f5f3"] { background:#f4f6fb!important; color:#4a5272!important; }
#pay-content span[style*="background:#1a1a1a"] { background:#1e2340!important; color:#fff!important; }
#pay-content button[style*="border:1.5px solid #F7C1C1"] { border-color:#fca5a5!important; color:#dc2626!important; }
#pay-content button[style*="background:#A32D2D"] { background:#dc2626!important; border-color:#dc2626!important; }
#pay-content td[style*="color:#888"][style*="font-size:12px"] { color:#7b85a8!important; }

/* ══ 일별 상세 뷰 ══ */
#pay-detail-inner { color:#1e2340; }
#pay-detail-inner button[style*="background:#f5f5f3"] { background:#f4f6fb!important; color:#4a5272!important; border:1px solid #dde2ee!important; }
#pay-detail-inner > div[style*="background:#fff"] { background:#fff!important; border-color:#dde2ee!important; box-shadow:0 2px 12px rgba(79,70,229,.06)!important; }
#pay-detail-inner [style*="background:#f8f8f6"] { background:#f4f6fb!important; }
#pay-detail-inner [style*="background:#FFF3E8"] { background:#fffbf0!important; }
#pay-detail-inner [style*="background:#E6F1FB"] { background:#eff6ff!important; border-color:#bfdbfe!important; }

/* 합계 카드 텍스트 */
#pay-detail-inner [style*="color:#555"] { color:#4a5272!important; }
#pay-detail-inner [style*="color:#185FA5"] { color:#1d4ed8!important; }
#pay-detail-inner [style*="color:#854F0B"] { color:#b45309!important; }
#pay-detail-inner [style*="color:#333"] { color:#1e2340!important; }
#pay-detail-inner [style*="color:#aaa"] { color:#a0abc8!important; }
#pay-detail-inner [style*="color:#888"] { color:#7b85a8!important; }

/* 날짜 테이블 */
#pay-detail-inner table { background:#fff; }
#pay-detail-inner td { border-color:#eef0f7!important; }
#pay-detail-inner tr[style*="background:#fff"] { background:#fff!important; }
#pay-detail-inner tr[style*="background:#F8F0FF"] { background:#faf5ff!important; }
#pay-detail-inner tr[style*="background:#FFF8F0"] { background:#fffbf0!important; }
#pay-detail-inner tr[style*="background:#F0F9FF"] { background:#f0f9ff!important; }
#pay-detail-inner tr[style*="background:#f0f0ec"] { background:#f4f6fb!important; }

/* 요일 배지 */
#pay-detail-inner span[style*="background:#FCEBEB"] { background:#fee2e2!important; }
#pay-detail-inner span[style*="background:#E6F1FB"] { background:#dbeafe!important; }
#pay-detail-inner span[style*="background:#f0f0ec"] { background:#eef0f7!important; }

/* 시간 인풋 */
#pay-detail-inner input[type="text"][id^="inp-"] {
  background:#f8f9fd!important; color:#1e2340!important;
  border-color:#dde2ee!important;
}
#pay-detail-inner input[type="text"][style*="background:#EBF4FF"] {
  background:#dbeafe!important; color:#1d4ed8!important; border-color:#3b82f6!important;
}

/* 색상 텍스트 */
#pay-detail-inner [style*="color:#bbb"] { color:#a0abc8!important; }
#pay-detail-inner [style*="color:#ddd"] { color:#c5cae0!important; }
#pay-detail-inner [style*="color:#ccc"] { color:#c5cae0!important; }
#pay-detail-inner [style*="color:#e0e0e0"] { color:#dde2ee!important; }

/* 합계 행 */
#pay-detail-inner tr[style*="background:#f0f0ec"] td { background:#f4f6fb!important; color:#1e2340!important; }

/* 버튼들 */
#pay-detail-inner button[style*="background:#f0f0ec"] { background:#f4f6fb!important; color:#4a5272!important; border:1px solid #dde2ee!important; }
#pay-detail-inner button[style*="background:#1a1a1a"] { background:#1e2340!important; color:#fff!important; }

/* 시간외 배지 */
#pay-detail-inner [style*="background:#E6F1FB"][style*="color:#185FA5"] { background:#dbeafe!important; color:#1d4ed8!important; }
#pay-detail-inner [style*="background:#EEEDFE"][style*="color:#534AB7"] { background:#ede9fe!important; color:#5b21b6!important; }
#pay-detail-inner [style*="background:#1a1a2e"] { background:#1e1b4b!important; }
#pay-detail-inner [style*="background:#FCEBEB"][style*="color:#A32D2D"] { background:#fee2e2!important; color:#991b1b!important; }
#pay-detail-inner input#ds-absent-inp { background:#f8f9fd!important; color:#b45309!important; }
#pay-detail-inner button[style*="background:#FFF0F0"] { background:#fef2f2!important; color:#dc2626!important; border-color:#fca5a5!important; }

/* ══ 통계(rank) 탭 ══ */
#rank-summary .scard { background:#fff!important; border-color:#dde2ee!important; }
#rank-content table { background:#fff; }
#rank-content thead tr { background:#f8f9fd!important; }
#rank-content thead th { color:#7b85a8!important; border-color:#dde2ee!important; }
#rank-content tbody tr { border-color:#eef0f7!important; }
#rank-content tbody td { color:#1e2340!important; border-color:#eef0f7!important; }
#rank-content [style*="background:#FFFDE7"] { background:#fefce8!important; }
#rank-content [style*="background:#F1F8E9"] { background:#f0fdf4!important; }
#rank-content [style*="background:#FFF3E8"] { background:#fffbf0!important; }
#rank-content [style*="background:#EBF4FF"] { background:#eff6ff!important; }
#rank-content [style*="background:#FCEBEB"] { background:#fee2e2!important; color:#991b1b!important; }
#rank-content [style*="background:#eee"] { background:#eef0f7!important; }
#rank-content [style*="background:#b0c8e8"] { background:#bfdbfe!important; }
#rank-content [style*="background:#185FA5"] { background:#2563eb!important; }
</style>
"""

NEW_HEADER = """<div class="app">
  <div class="app-header">
    <div style="display:flex;align-items:center;gap:10px">
      <div style="width:38px;height:38px;border-radius:10px;background:linear-gradient(135deg,#6c63ff,#ff6584);display:flex;align-items:center;justify-content:center;font-size:18px;flex-shrink:0">🎬</div>
      <div>
        <h1>KBS 보도영상국 파견인력 관리 시스템</h1>
        <div style="font-size:11px;color:var(--text3);margin-top:2px">뉴스영상콘텐츠부 · 인제스트 &amp; 촬영보조</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;margin-left:auto">
      <span id="sync-indicator" style="display:none;align-items:center;gap:5px;font-size:11px;color:var(--green);background:rgba(34,197,94,.1);padding:4px 10px;border-radius:20px;border:1px solid rgba(34,197,94,.2)">
        <span style="width:6px;height:6px;border-radius:50%;background:var(--green);display:inline-block;animation:pulse 2s infinite"></span>자동동기화
      </span>
      <span id="save-status" style="font-size:11px;color:var(--text3)"></span>
      <button onclick="openDataMgr()" style="padding:7px 14px;background:var(--surface2);border:1px solid var(--border);border-radius:9px;font-size:12px;cursor:pointer;color:var(--text2);font-weight:500;font-family:inherit">💾 데이터 관리</button>
    </div>
  </div>

  <div class="tabs">
    <button class="tab active" onclick="showPage('list')">직원 현황</button>
    <button class="tab" onclick="showPage('history')">교체 이력</button>
    <button class="tab" onclick="showPage('agency')">파견업체</button>
    <button class="tab" onclick="showPage('pay')">파견료 정산</button>
    <button class="tab" onclick="showPage('rank')">📊 통계</button>
  </div>
"""

# Rebuild the body HTML: replace the original app-header+tabs with our new ones
# Find where the main pages start (after the closing </div> of app-header tabs section)
# Strategy: replace content from <div class="app"> up to the first page div

# Find position of first page div in body_html
page_list_idx = body_html.find('<div id="page-list"')
app_end_html = body_html[page_list_idx:]  # pages + modals

new_body = NEW_HEADER + app_end_html

# Build final HTML
html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>KBS 보도영상국 파견인력 관리 시스템</title>
<meta name="description" content="KBS 보도영상국 파견직 인력 현황 및 파견료 정산 관리 시스템">
<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
{NEW_CSS}
</head>
<body>
{new_body}
{js_block}
{after_html}
</body>
</html>"""

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print(f'Done. index.html = {len(html):,} bytes')

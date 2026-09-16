import re

with open("frontend/index.html", "r", encoding="utf-8") as f:
    content = f.read()

replacements = [
    ('class="h-full bg-slate-950 text-slate-100"', 'class="h-full bg-slate-50 text-slate-900"'),
    ('::-webkit-scrollbar-track { background: #0f172a; }', '::-webkit-scrollbar-track { background: #f8fafc; }'),
    ('::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }', '::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 4px; }'),
    ('border-b border-slate-800 bg-slate-900/80 backdrop-blur', 'border-b border-slate-200 bg-white/95 backdrop-blur shadow-xs'),
    ('bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent', 'text-slate-900'),
    ('bg-slate-800/80 border border-slate-700', 'bg-slate-100 border border-slate-200'),
    ('bg-slate-900 text-white', 'bg-white text-slate-900'),
    ('bg-emerald-950/50 border-emerald-700 text-emerald-300', 'bg-emerald-50 border-emerald-300 text-emerald-800'),
    ('bg-indigo-950/40 border-indigo-700 text-indigo-300', 'bg-indigo-50 border-indigo-200 text-indigo-700'),
    ('bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200', 'bg-slate-900 hover:bg-slate-800 text-white shadow-xs'),
    ('bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-sm', 'bg-white border border-slate-200 rounded-xl p-4 shadow-sm'),
    ('bg-slate-900/90 border border-slate-800 rounded-2xl p-6 shadow-xl', 'bg-white border border-slate-200 rounded-2xl p-6 shadow-sm'),
    ('bg-slate-900/90 border border-slate-800 rounded-xl p-5', 'bg-white border border-slate-200 rounded-xl p-5 shadow-xs'),
    ('bg-slate-900/90 border border-slate-800 rounded-xl overflow', 'bg-white border border-slate-200 rounded-xl overflow shadow-xs'),
    ('bg-red-950/30 border border-red-900/50', 'bg-red-50/60 border border-red-200'),
    ('bg-slate-950/80 border rounded-xl p-4', 'bg-slate-50 border rounded-xl p-4'),
    ('border-red-900/60 bg-gradient-to-b from-slate-950 to-red-950/10', 'border-2 border-red-200 bg-red-50/40'),
    ('border-slate-800', 'border-slate-200'),
    ('bg-slate-950', 'bg-slate-50'),
    ('bg-slate-900', 'bg-white'),
    ('text-white', 'text-slate-900'),
    ('text-slate-400', 'text-slate-500'),
    ('text-slate-300', 'text-slate-700'),
    ('text-slate-200', 'text-slate-800'),
    ('bg-slate-800', 'bg-slate-100'),
    ('bg-slate-700', 'bg-slate-200'),
    ('hover:bg-slate-800/40', 'hover:bg-slate-50'),
    ('hover:bg-slate-800/30', 'hover:bg-slate-50'),
    ('divide-slate-800/60', 'divide-slate-100'),
    ('divide-slate-800', 'divide-slate-100'),
    ('bg-indigo-950', 'bg-indigo-100'),
    ('bg-emerald-950', 'bg-emerald-100'),
    ('bg-red-950', 'bg-red-100'),
    ('text-indigo-400', 'text-indigo-600'),
    ('text-emerald-400', 'text-emerald-600'),
    ('text-red-400', 'text-red-600'),
    ('text-amber-400', 'text-amber-700'),
    ('bg-indigo-600', 'bg-indigo-600 text-white'),
    ('bg-emerald-600', 'bg-emerald-600 text-white')
]

for src, dst in replacements:
    content = content.replace(src, dst)

with open("frontend/index.html", "w", encoding="utf-8") as f:
    f.write(content)

print("Theme updated to white background successfully!")

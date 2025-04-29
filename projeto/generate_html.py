from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

def generate_html_report(code, builder, nesting_counter, ifs_simples):
    analysis = builder.symbol_table.get_analysis()

    html = """
    <html>
    <head>
        <title>Relatório de Análise</title>
        <style>
            body { background: #111; color: #eee; font-family: monospace; padding: 2em; }
            h2 { color: #ff00cc; }
            .section { margin-bottom: 3em; }
            table { border-collapse: collapse; width: 100%; margin-top: 1em; }
            th, td { border: 1px solid #444; padding: 8px; text-align: left; }
            th { background: #222; color: #ff99ff; }
            .error { color: #ff6666; }
            .warn { color: #ffcc66; }
            .if-simp { color: #66ffcc; }
            pre { background: #1e1e1e; padding: 1em; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>Relatório de Análise de Código</h1>

        <div class="section">
            <h2>1. Código Fonte</h2>
            <pre>{code}</pre>
        </div>

        <div class="section">
            <h2>2. Tabela de Símbolos</h2>
            <table>
                <tr><th>ID</th><th>Scope</th><th>Type</th></tr>
    """

    for simb in builder.symbol_table.symbols.values():
        html += f"<tr><td>{simb.name}</td><td>{simb.scope}</td><td>{simb.type}</td></tr>\n"

    html += """
            </table>
        </div>

        <div class="section">
            <h2>3. Contagens</h2>
            <ul>
                <li>Declarações: {decl}</li>
                <li>Atribuições: {attr}</li>
                <li>Leitura/Escrita: {rw}</li>
                <li>Condicionais: {cond}</li>
                <li>Cíclicas: {cycle}</li>
                <li>Aninhamentos: {nest}</li>
                <li>Ifs simplificáveis: {ifs}</li>
            </ul>
        </div>
    """.format(
        decl=builder.declaration_count,
        attr=builder.assignment_count,
        rw=builder.read_write_count,
        cond=builder.conditional_count,
        cycle=builder.cyclic_count,
        nest=nesting_counter.aninhamentos,
        ifs=ifs_simples.otimizavel
    )

    html += """
        <div class="section">
            <h2>4. Erros e Warnings</h2>
    """

    if analysis["redeclared"]:
        for var in analysis["redeclared"]:
            html += f"<p class='error'>[ERROR] Variável {var.name} redeclarada (linha {var.line})</p>"

    for var in analysis["undeclared"]:
        html += f"<p class='error'>[ERROR] Variável {var[0]} não declarada (linha {var[1]})</p>"

    for var in analysis["unused"]:
        html += f"<p class='warn'>[WARNING] Variável {var.name} declarada mas não usada (linha {var.line})</p>"

    for var in analysis["uninitialized_but_used"]:
        html += f"<p class='warn'>[WARNING] Variável {var.name} usada sem inicializar (linha {var.line})</p>"

    html += "</div><div class='section'><h2>5. Tipos</h2><table><tr><th>Tipo</th><th>Quantidade</th></tr>"
    for type_spec, count in analysis["type_counts"].items():
        html += f"<tr><td>{type_spec}</td><td>{count}</td></tr>"
    html += "</table></div>"

    html += """
        <div class='section'>
            <h2>6. Estruturas de Controlo Aninhadas</h2>
            <p class='if-simp'>Total: {}</p>
        </div>
    """.format(nesting_counter.aninhamentos)

    html += """
        <div class='section'>
            <h2>7. IFs simplificáveis</h2>
            <p class='if-simp'>Total: {}</p>
        </div>
    """.format(ifs_simples.otimizavel)


    html += "</body></html>"

    formatter = HtmlFormatter(style="monokai", noclasses=True)
    highlighted_code = highlight(code, PythonLexer(), formatter)
    html = html.replace("{code}", highlighted_code)

    with open("relatorio.html", "w") as f:
        f.write(html)

    print("Relatório HTML gerado: relatorio.html")

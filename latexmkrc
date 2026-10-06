# Receta de compilacion para el TFG.
# Ciclo previsto: pdflatex -> bibtex -> pdflatex -> pdflatex.
# Se limita el numero maximo de pasadas para evitar bucles largos en Overleaf.

$pdf_mode = 1;              # 1 = pdflatex  (OJO: 5 era xelatex+xdvipdfmx, no pdflatex)
$bibtex_use = 1;            # ejecutar bibtex solo cuando el .bbl este ausente o desactualizado
$max_repeat = 3;            # pasadas suficientes una vez estabilizadas las citas y referencias

# Detener el proceso ante el primer error real en lugar de seguir compilando.
$pdflatex = 'pdflatex -file-line-error -interaction=nonstopmode -halt-on-error %O %S';
$bibtex = 'bibtex %O %B';

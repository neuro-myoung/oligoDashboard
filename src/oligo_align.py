import polars as pl
import altair as alt

def oligoAlign(df, align='position'):
    circle_diameter = 25  # Approximate visual diameter for size=500 circles
    xpadding = 20  # Small padding for axes/labels

    # Determine plot scale
    maxWidth = df.select(pl.col(align).max()).item() - df.select(pl.col(align).min()).item()
    y_idx = {name: i*1.2+0.5 for i, name in enumerate(df.select(pl.col("compound_id").unique()).to_series())}
    maxHeight = len(y_idx.keys())


    ypadding = 10*maxHeight  # Small padding for axes/labels

    chart_width = maxWidth * circle_diameter + xpadding
    chart_height = maxHeight * circle_diameter + ypadding


    mapped_df = pl.DataFrame({
        "compound_id": list(y_idx.keys()),
        "y_coord": list(y_idx.values())
    })

    df = df.join(mapped_df, on="compound_id", how="right")

    chart = alt.Chart(df)

    circles = chart.mark_circle(
        size=500,
        stroke='black',
        strokeWidth=2,
    ).encode(
        x=alt.X(align+':O', axis=None),
        y=alt.Y('y_coord:Q', axis=None),
        color=alt.Color('base:N',
                         scale=alt.Scale(scheme='pastel1')),
        strokeWidth = alt.value(2),
        stroke = alt.value("black"),
        strokeDash=alt.StrokeDash('linker:N',  # Dash pattern based on linker
                                  scale=alt.Scale(
                                      range=[[0,1], [1,0], [5,5]]  # Different dash patterns
                                  )),
        tooltip=['position:O', 'nucleotide:N', 'compound_id:N', 'sugar:N', 'base:N']
    )

    text = chart.mark_text(
        align='center',
        baseline='middle',
        fontSize=12,  
        fontWeight='bold'
    ).encode(
        x=alt.X('position:O', axis=None),
        y=alt.Y('y_coord:Q', axis=None),
        text='base:N',
        color=alt.value('black')
    )
   
    chart = (circles + text).properties(
        width=chart_width,
        height=chart_height,
    ).configure_view(
        stroke=None,
        fill='white'
    )

    return chart
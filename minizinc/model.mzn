% Data
int: N;
array[1..N] of int: lengths;
array[1..N] of int: widths;
array[1..N] of int: height;
array[1..N] of int: reds;
array[1..N] of int: greens;
array[1..N] of int: blues;

% Variables
array[1..N] of var 0..1000000: x;
array[1..N] of var 0..1000000: y;
array[1..N] of var 0..1000000: z;


% Add your constraints
% Add the objective


% Output in JSON format for blockviz
% Remark: you might need blockviz flag --permissive-io
output [
    "{\"boxes\": [",
    join(
        ", ",
        [
            concat([
                "{\"color\": [", show(reds[i]), ", ", show(greens[i]), ", ", show(blues[i]), "], ",
                "\"position\": [", show(x[i]), ", ", show(y[i]), ", ", show(z[i]), "], ",
                "\"size\": [", show(lengths[i]), ", ", show(widths[i]), ", ", show(height[i]), "]",
                "}"
            ])
            | i in 1..N
        ]
    ),
    "],\"text\": \"Solution ",
    show(objective),
    "\\nSize ",
    show(total_x),
    " x ",
    show(total_y),
    " x ",
    show(total_z),
    "\\nObjective ",
    show(objective),
    "\"}\n"
];

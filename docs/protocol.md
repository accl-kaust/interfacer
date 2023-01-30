Various protocols are supported by Interfacer, with support for additional buses possible using the `protocols.json` overrides.

## AXI Stream

**AXI4-Stream** (AXIS) is an AMBA 4 protocol designed to transport streams of data of arbitrary widths (8n). 

??? example "Example"
    wavedrom (
     { signal: [
    {    name: 'aclk',   wave: 'p.............'},
    {    name: 'aresetn',   wave: '01............'},
    ['Master',
      ['ctrl',
          {name: 'strb', wave: '0.............'},
          {name: 'keep', wave: '0.............'},
          {name: 'id', wave: '0.............'},
          {name: 'dest', wave: '0.............'},
          {name: 'user', wave: '0.............'},
          {name: 'last', wave: '0......10.....'},
          {name: 'valid', wave: '0..1....0.....'},
      ],
      ['data',
          {  name: 'data',  wave: 'x..3.x.4x.....', data: 'A1 A2'},
      ]
    ],
    {},
      ['Slave',
        ['ctrl',
          {name: 'ready',   wave: '0.1..0.1......'},
        ],
        ['data',
            {  name: 'data',  wave: 'x..3.x.4x.....', data: 'A1 A2'},
        ]
      ]
    ],
    head:{
      text:'AXI Stream Example',
      tick:0,
    },
    foot:{
      text:'Figure 1',
      tock:10
    },
    config: { hscale: 1 }
    }
    )

??? info "Bus Info"
    ### Data

    **n** - Data bus width in bytes.

    ### ID

    **i** - TID width. Recommended maximum is 8-bits.

    ### Dest

    **d** - TDEST width. Recommended maximum is 4-bits.

    ### User

    **u** - TUSER width. Recommended number of bits is an integer multiple of the width of the interface in bytes.

## AXI Full

??? example "Example"
    wavedrom (
     { signal: [
    {    name: 'aclk',   wave: 'p.............'},
    {    name: 'aresetn',   wave: '01............'},
    ['Master',
      ['ctrl',
          {name: 'strb', wave: '0.............'},
          {name: 'keep', wave: '0.............'},
          {name: 'id', wave: '0.............'},
          {name: 'dest', wave: '0.............'},
          {name: 'user', wave: '0.............'},
          {name: 'last', wave: '0......10.....'},
          {name: 'valid', wave: '0..1....0.....'},
      ],
      ['data',
          {  name: 'data',  wave: 'x..3.x.4x.....', data: 'A1 A2'},
      ]
    ],
    {},
      ['Slave',
        ['ctrl',
          {name: 'ready',   wave: '0.1..0.1......'},
        ],
        ['data',
            {  name: 'data',  wave: 'x..3.x.4x.....', data: 'A1 A2'},
        ]
      ]
    ],
    head:{
      text:'AXI Stream Example',
      tick:0,
    },
    foot:{
      text:'Figure 1',
      tock:10
    },
    config: { hscale: 1 }
    }
    )

??? info "Bus Info"
    ### Data

    **n** - Data bus width in bytes.

    ### ID

    **i** - TID width. Recommended maximum is 8-bits.

    ### Dest

    **d** - TDEST width. Recommended maximum is 4-bits.

    ### User

    **u** - TUSER width. Recommended number of bits is an integer multiple of the width of the interface in bytes.

## AXI Lite

??? example "Example"
    wavedrom (
     { signal: [
    {    name: 'aclk',   wave: 'p.............'},
    {    name: 'aresetn',   wave: '01............'},
    ['Master',
      ['ctrl',
          {name: 'strb', wave: '0.............'},
          {name: 'keep', wave: '0.............'},
          {name: 'id', wave: '0.............'},
          {name: 'dest', wave: '0.............'},
          {name: 'user', wave: '0.............'},
          {name: 'last', wave: '0......10.....'},
          {name: 'valid', wave: '0..1....0.....'},
      ],
      ['data',
          {  name: 'data',  wave: 'x..3.x.4x.....', data: 'A1 A2'},
      ]
    ],
    {},
      ['Slave',
        ['ctrl',
          {name: 'ready',   wave: '0.1..0.1......'},
        ],
        ['data',
            {  name: 'data',  wave: 'x..3.x.4x.....', data: 'A1 A2'},
        ]
      ]
    ],
    head:{
      text:'AXI Stream Example',
      tick:0,
    },
    foot:{
      text:'Figure 1',
      tock:10
    },
    config: { hscale: 1 }
    }
    )

??? info "Bus Info"
    ### Data

    **n** - Data bus width in bytes.

    ### ID

    **i** - TID width. Recommended maximum is 8-bits.

    ### Dest

    **d** - TDEST width. Recommended maximum is 4-bits.

    ### User

    **u** - TUSER width. Recommended number of bits is an integer multiple of the width of the interface in bytes.
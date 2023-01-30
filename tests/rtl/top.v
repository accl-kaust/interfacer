module blinky_zybo_z7
  #(parameter random = 16,
  parameter blah = 2)
  (input wire  clk,
   input wire rst,
   input wire ce,
   input wire [1:0] fatr,
   output wire [((2+random)/(blah)):4] TREADY,
   input wire [((2+random)/(blah)):4] tdata,
   input wire [((2+random)/(blah)):4] thing
   );

   blinky #(.clk_freq_hz (125_000_000)) blinky_1
     (.clk (clk),
      .q   (q));

   blinky #(.clk_freq_hz (125_000_000)) blinky
     (.clk (clk),
      .q   (q));

endmodule


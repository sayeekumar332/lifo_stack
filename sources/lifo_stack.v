`timescale 1ns/1ns
module stack_pointer (
  input wire clk,
  input wire rst,
  input wire push,
  input wire pop,
  output wire [4:0] stack_addr,
  output wire full,
  output wire empty
);
 // TODO : Impelement the stack pointer logic
endmodule

`timescale 1ns/1ns
module stack_ram (
  input wire clk,
  input wire  [4:0] stack_addr,
  input wire  [3:0] stack_data_in,
  input wire  stack_we,
  input wire  stack_re,
  output wire [3:0] stack_data_out
);

  // TODO : Implement the stack ram logic
endmodule

`timescale 1ns/1ns
module stack_data_mux (
  input  wire [3:0] data_in,
  input  wire [3:0] pc_in,
  input  wire stack_mux_sel,
  output wire [3:0] stack_mux_out
);
   // TODO : Implement the stack mux logic
endmodule

`timescale 1ns/1ns
module lifo_stack (
  input  wire clk,
  input  wire [3:0] stack_data_1_in,
  input  wire [3:0] stack_data_2_in,
  input  wire stack_reset,
  input  wire stack_push,
  input  wire stack_pop,
  input  wire stack_mux_sel,
  input  wire stack_we,
  input  wire stack_re,
  output wire [3:0] stack_data_out,
  output wire full_o,
  output wire empty_o
);

   // TODO : Implement the instances with the correct wiring with lifo_stack top module
endmodule

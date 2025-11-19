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
reg [4:0] stack_addr_reg;
reg full_r;
reg empty_r;
assign full_r     = (stack_addr_reg == 5'b10000);
assign empty_r    = (stack_addr_reg == 5'b00000);
always@(posedge clk) begin
   if(rst)
     stack_addr_reg <= 5'b00000;
   else if(push && !full_r) begin
     stack_addr_reg <= stack_addr_reg + 5'b00001;
   end else if(pop && !empty_r) begin
     stack_addr_reg <= stack_addr_reg - 5'b00001;
   end 
   
end
assign full       = full_r;
assign empty      = empty_r;
assign stack_addr = stack_addr_reg; 
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

reg [3:0] stack_arr [16:0];
always@(posedge clk) begin
  if(stack_we) begin
    stack_arr[stack_addr] = stack_data_in;
  end
end

assign stack_data_out = stack_re ? stack_arr[stack_addr] : '0; 
endmodule

`timescale 1ns/1ns
module stack_data_mux (
  input  wire [3:0] data_in,
  input  wire [3:0] pc_in,
  input  wire stack_mux_sel,
  output wire [3:0] stack_mux_out
);
assign stack_mux_out = stack_mux_sel ? data_in : pc_in;
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

wire [3:0] stack_data_in_w;
wire [4:0] stack_addr_w;

stack_data_mux dut_1(
    .data_in       (stack_data_1_in),
    .pc_in         (stack_data_2_in),
    .stack_mux_sel (stack_mux_sel),
    .stack_mux_out (stack_data_in_w)
);

stack_pointer dut_2 (
     .clk        (clk),
     .rst        (stack_reset),
     .push       (stack_push),
     .pop        (stack_pop),
     .stack_addr (stack_addr_w),
     .full       (full_o),
     .empty      (empty_o)
);

stack_ram dut_3 (
     .clk            (clk),
     .stack_addr     (stack_addr_w),
     .stack_data_in  (stack_data_in_w),
     .stack_we       (stack_we),
     .stack_re       (stack_re),
     .stack_data_out (stack_data_out)
);
endmodule

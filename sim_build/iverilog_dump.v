module iverilog_dump();
initial begin
    $dumpfile("lifo_stack.fst");
    $dumpvars(0, lifo_stack);
end
endmodule

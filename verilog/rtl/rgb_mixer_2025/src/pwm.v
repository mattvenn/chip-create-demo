`default_nettype none
`timescale 1ns/1ns
module pwm #(
    parameter WIDTH = 8,
    parameter INVERT = 0
    ) (
    input wire clk,
    input wire reset,
    output reg out,
    input wire [WIDTH-1:0] level
    );

    reg [WIDTH-1:0] count;
    wire pwm_on = count < level;

    always @(posedge clk) begin
        if(reset)
            count <= 1'b0;
        else
            count <= count + 1'b1;
    end

    always @(posedge clk) begin
	if(reset)
            out <= 1'b0;
        else if(INVERT)
	    out <= ! pwm_on;
        else
            out <= pwm_on;
    end

endmodule

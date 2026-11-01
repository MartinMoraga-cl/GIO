n = 14; % no pasarse de 14...
m = n*n;

Q = m*eye(n);
for i=1:n
  for j=(i+1):n
    Q(i,j) = rand();
  endfor
endfor
Q = Q + Q' - diag(diag(Q))

min = Inf;
xmin = zeros(n);
xminb = zeros(n);
for i = 1:(2^n)
  xi = 2 * (dec2bin(i-1, n) - '0')' - 1;
  val = xi' * Q * xi;
  if (val<min)
    min = val;
    xmin=xi;
  elseif (val==min)
    xminb=xi;
  end
  disp(val);
endfor
disp("\n")
disp(min)
disp(xmin)
disp(" ")
disp(xminb)

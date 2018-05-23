SELECT CUSTOMER.FirstName, CUSTOMER.LastName, i.TotalAmount
FROM CUSTOMER 
INNER JOIN
(
  SELECT INVOICE.CustomerNumber, INVOICE.TotalAmount
  FROM INVOICE and INVOICE_ITEM
  WHERE INVOICE.InvoiceNumber = INVOICE_ITEM.InvoiceNumber
  AND INVOICE_ITEM.Item = “Dress Shirt”
) as i
ON CUSTOMER.CustomerID  = i.CustomerNumber
ORDER BY CUSTOMER.LastName ASC, CUSTOMER.FirstName DESC
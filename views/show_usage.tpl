<!doctype html>
<html>
<head>
<title>Usage</title>
</head>
<body>
<table>
%for row in data:
    <tr>
    %for cell in row:
        <td>{{ cell }}</td>
    %end
    </tr>
%end
</table>
</body>
</html>

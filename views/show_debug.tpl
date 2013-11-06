<!doctype html>
<html>
<head><title>Debug</title>
</head>
<body>
<table>
%for v in tx.iteritems():
    <tr>
    <td>
    {{ v[0] }}
    </td>
    <td>
     {{ v[1] }}
    </td>
    </tr>
%end
</table>
<table>
%for v in rx.iteritems():
    <tr>
    <td>
    {{ v[0] }}
    </td>
    <td>
     {{ v[1] }}
    </td>
    </tr>
%end
</table>
</body>
</html>

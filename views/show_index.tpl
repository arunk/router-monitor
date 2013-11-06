<!doctype html>
<html>
<head>
    <title>Broadband Usage Stats</title>
</head>
<body>
<table>
<thead>
    <tr>
        <th>
            %if is_prev:
                <a href="/{{ ago+1 }}/">Previous</a>
            %end
        </th>
        <th>Cycle Usage</th>
        <th>
            %if is_next:
                <a href="/{{ ago-1 }}/">Next</a>
            %end
        </th>
    </tr>
</thead>
<tbody>
<tr>
    <td>From date:</td>
    <td>{{ from_date }}</td>
</tr>
<tr>
    <td>Transmitted</td>
    <td>{{ totaltx }}</td>
</tr>
<tr>
    <td>Received</td>
    <td>{{ totalrx }}</td>
</tr>
<tr>
    <td>Total</td>
    <td>{{ total }}</td>
</tr>
</tbody>
</table>

%tdy_img_src = "/img/plot/{0}/{1:02d}/{2:02d}.png".format(for_date.year, for_date.month, for_date.day)
<h4>To date:</h4>
<img src="{{ tdy_img_src }}">
</body>
</html>

# Python
import csv
# Django
from django.http import StreamingHttpResponse

class CSVBuffer:
    def write(self, value):
        return value

class CSVStream:
    def export(self, filename, iterator, serializer):
        writer = csv.writer(CSVBuffer())

        response = StreamingHttpResponse((writer.writerow(serializer(data)) for data in iterator), content_type = 'text/csv')
        response['Content-Disposition'] = f"attachment; filename = {filename}.csv"

        return response

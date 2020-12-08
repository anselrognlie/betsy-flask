from decimal import Decimal, InvalidOperation
from wtforms.fields.core import DecimalField

class DollarField(DecimalField):
    def process_formdata(self, valuelist):
        # pylint: disable=attribute-defined-outside-init
        scrubbed = []
        if len(valuelist) == 1:
            stripped = valuelist[0].strip('$').replace(',', '')
            try:
                scrubbed = [str(int(Decimal(stripped) * 100))]
            except InvalidOperation:
                scrubbed = [valuelist[0]]

        # Calls "process_formdata" on the parent types of "DollarField",
        # which includes "DecimalField"
        super().process_formdata(scrubbed)

    def _value(self):
        try:
            return f"{(self.data / 100):.2f}"
        except TypeError:
            if self.raw_data is not None:
                return str(self.raw_data[0])
            else:
                return ""

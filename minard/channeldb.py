from wtforms import Form, BooleanField, StringField, validators, IntegerField
from detector_state import engine

class ChannelStatusForm(Form):
    crate =              IntegerField('crate', [validators.NumberRange(min=0,max=19)])
    slot =               IntegerField('slot', [validators.NumberRange(min=0,max=15)])
    channel =            IntegerField('channel', [validators.NumberRange(min=0,max=31)])
    pmt_removed =        BooleanField('PMT removed')
    pmt_reinstalled =    BooleanField('PMT reinstalled')
    low_occupancy =      BooleanField('Low Occupancy')
    zero_occupancy =     BooleanField('Zero Occupancy')
    screamer =           BooleanField('Screamer')
    bad_discriminator =  BooleanField('Bad Discriminator')
    no_n100 =            BooleanField('No N100')
    no_n20 =             BooleanField('No N20')
    no_esum =            BooleanField('No ESUM')
    cable_pulled =       BooleanField('Cable pulled')
    bad_cable =          BooleanField('Bad Cable')
    resistor_pulled =    BooleanField('Resistor pulled')
    disable_n100 =       BooleanField('Disable N100')
    disable_n20 =        BooleanField('Disable N20')
    bad_base_current =   BooleanField('Bad Base Current')
    name =               StringField('Name', [validators.Length(min=1)])
    info =               StringField('Info', [validators.Length(min=1)])

def get_channels(kwargs, limit=100):
    """
    Returns a list of the current channel statuses for multiple channels in the
    detector. `kwargs` should be a dictionary containing fields and their
    associated values to select on. For example, to select only channels that
    have low occupancy:

        >>> get_channels({'low_occupancy': True})

    `limit` should be the maximum number of records returned.
    """
    conn = engine.connect()

    fields = [field.name for field in ChannelStatusForm()]

    # make sure all the values in kwargs are actual fields
    kwargs = dict(item for item in kwargs.items() if item[0] in fields)

    query = "SELECT DISTINCT ON (crate, slot, channel) * FROM channeldb "
    if len(kwargs):
        query += "WHERE %s " % (" AND ".join(["%s = %%(%s)s" % (item[0], item[0]) for item in kwargs.items()]))
    query += "ORDER BY crate, slot, channel, timestamp DESC LIMIT %i" % limit

    result = conn.execute(query, kwargs)

    if result is None:
        return None

    keys = result.keys()
    rows = result.fetchall()

    return [dict(zip(keys,row)) for row in rows]

def get_channel_history(crate, slot, channel, limit=100):
    """
    Returns a list of the channel statuses for a single channel in the
    detector. `limit` is the maximum number of records to return.
    """
    conn = engine.connect()

    result = conn.execute("SELECT * FROM channeldb WHERE crate = %s AND slot = %s AND channel = %s ORDER BY timestamp DESC LIMIT %s", (crate,slot,channel,limit))

    if result is None:
        return None

    keys = result.keys()
    rows = result.fetchall()

    return [dict(zip(keys,row)) for row in rows]

def get_pmt_info(crate, slot, channel):
    """
    Returns a dictionary of the pmt info for a given channel.
    """
    conn = engine.connect()

    result = conn.execute("SELECT * FROM pmt_info WHERE crate = %s AND slot = %s AND channel = %s", (crate, slot, channel))

    if result is None:
        return None

    keys = result.keys()
    row = result.fetchone()

    if row is None:
        return None

    return dict(zip(keys,row))

def get_channel_status(crate, slot, channel):
    """
    Returns a dictionary of the channel status for a single channel in the detector.
    """
    conn = engine.connect()

    result = conn.execute("SELECT * FROM channeldb WHERE crate = %s AND slot = %s AND channel = %s ORDER BY timestamp DESC LIMIT 1", (crate,slot,channel))

    if result is None:
        return None

    keys = result.keys()
    row = result.fetchone()

    return dict(zip(keys,row))

def get_channel_status_form(crate, slot, channel):
    """
    Returns a channel status form filled in with the current channel status for
    a single channel in the detector.
    """
    return ChannelStatusForm(**get_channel_status(crate, slot, channel))

def upload_channel_status(form):
    """
    Upload a new channel status record in the database.
    """
    conn = engine.connect()
    result = conn.execute("INSERT INTO channeldb (crate, slot, channel, pmt_removed, pmt_reinstalled, low_occupancy, zero_occupancy, screamer, bad_discriminator, no_n100, no_n20, no_esum, cable_pulled, bad_cable, resistor_pulled, disable_n100, disable_n20, bad_base_current, name, info) VALUES (%(crate)s, %(slot)s, %(channel)s, %(pmt_removed)s, %(pmt_reinstalled)s, %(low_occupancy)s, %(zero_occupancy)s, %(screamer)s, %(bad_discriminator)s, %(no_n100)s, %(no_n20)s, %(no_esum)s, %(cable_pulled)s, %(bad_cable)s, %(resistor_pulled)s, %(disable_n100)s, %(disable_n20)s, %(bad_base_current)s, %(name)s, %(info)s)", **form.data)
    return result

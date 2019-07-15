from flask_login import  LoginManager, UserMixin, login_required, login_user, logout_user 


class User(UserMixin):

  def __init__(self, email):
    self.id = email
      
  def __repr__(self):
    return "%s/%s" % (self.id)

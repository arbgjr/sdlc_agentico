#!/usr/bin/env python3
"""
Integration tests for Ruby on Rails project analysis.

Tests the full sdlc-import workflow on a sample Ruby project.
"""

import sys
import pytest
import tempfile
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent.parent / ".claude/lib/python"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scripts"))

from project_analyzer import ProjectAnalyzer


def create_file(path: Path, content: str):
    """Helper to create file with content"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


@pytest.fixture
def rails_project():
    """Create a minimal Ruby on Rails project structure"""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_path = Path(tmpdir)

        # Create Gemfile
        create_file(
            project_path / "Gemfile",
            """source 'https://rubygems.org'
git_source(:github) { |repo| "https://github.com/#{repo}.git" }

ruby '3.2.0'

gem 'rails', '~> 7.1.0'
gem 'pg', '~> 1.5'
gem 'puma', '~> 6.0'
gem 'redis', '~> 5.0'
gem 'bcrypt', '~> 3.1.7'
gem 'jwt', '~> 2.7'
gem 'rack-cors'

group :development, :test do
  gem 'debug'
  gem 'rspec-rails', '~> 6.0'
  gem 'factory_bot_rails'
  gem 'faker'
end

group :development do
  gem 'rubocop', require: false
  gem 'rubocop-rails', require: false
end

group :test do
  gem 'shoulda-matchers', '~> 5.0'
  gem 'database_cleaner-active_record'
end
"""
        )

        # Create config/database.yml
        create_file(
            project_path / "config/database.yml",
            """default: &default
  adapter: postgresql
  encoding: unicode
  pool: <%= ENV.fetch("RAILS_MAX_THREADS") { 5 } %>
  host: <%= ENV['DB_HOST'] || 'localhost' %>
  port: <%= ENV['DB_PORT'] || 5432 %>
  username: <%= ENV['DB_USER'] || 'postgres' %>
  password: <%= ENV['DB_PASSWORD'] %>

development:
  <<: *default
  database: <%= ENV['DB_NAME'] || 'myapp_development' %>

test:
  <<: *default
  database: <%= ENV['DB_NAME_TEST'] || 'myapp_test' %>

production:
  <<: *default
  database: <%= ENV['DB_NAME'] || 'myapp_production' %>
"""
        )

        # Create config/application.rb
        create_file(
            project_path / "config/application.rb",
            """require_relative "boot"

require "rails"
require "active_model/railtie"
require "active_job/railtie"
require "active_record/railtie"
require "action_controller/railtie"
require "action_mailer/railtie"

Bundler.require(*Rails.groups)

module MyApp
  class Application < Rails::Application
    config.load_defaults 7.1
    config.api_only = true

    # CORS configuration
    config.middleware.insert_before 0, Rack::Cors do
      allow do
        origins '*'
        resource '*',
          headers: :any,
          methods: [:get, :post, :put, :patch, :delete, :options, :head]
      end
    end
  end
end
"""
        )

        # Create User model
        create_file(
            project_path / "app/models/user.rb",
            """class User < ApplicationRecord
  has_secure_password

  validates :email, presence: true, uniqueness: true
  validates :username, presence: true, uniqueness: true
  validates :password, length: { minimum: 8 }, if: -> { password.present? }

  has_many :posts, dependent: :destroy

  enum role: { user: 0, admin: 1 }

  def generate_jwt_token
    JWT.encode(
      {
        user_id: id,
        email: email,
        role: role,
        exp: 24.hours.from_now.to_i
      },
      Rails.application.credentials.secret_key_base
    )
  end

  def self.from_token(token)
    decoded = JWT.decode(
      token,
      Rails.application.credentials.secret_key_base
    ).first
    find(decoded['user_id'])
  rescue JWT::DecodeError, ActiveRecord::RecordNotFound
    nil
  end
end
"""
        )

        # Create Post model
        create_file(
            project_path / "app/models/post.rb",
            """class Post < ApplicationRecord
  belongs_to :user

  validates :title, presence: true, length: { maximum: 255 }
  validates :content, presence: true
  validates :user, presence: true

  scope :published, -> { where(published: true) }
  scope :recent, -> { order(created_at: :desc) }
end
"""
        )

        # Create migration
        create_file(
            project_path / "db/migrate/20240101000000_create_users.rb",
            """class CreateUsers < ActiveRecord::Migration[7.1]
  def change
    create_table :users do |t|
      t.string :username, null: false
      t.string :email, null: false
      t.string :password_digest, null: false
      t.integer :role, default: 0, null: false

      t.timestamps
    end

    add_index :users, :username, unique: true
    add_index :users, :email, unique: true
  end
end
"""
        )

        create_file(
            project_path / "db/migrate/20240101000001_create_posts.rb",
            """class CreatePosts < ActiveRecord::Migration[7.1]
  def change
    create_table :posts do |t|
      t.string :title, null: false
      t.text :content, null: false
      t.boolean :published, default: false, null: false
      t.references :user, null: false, foreign_key: true

      t.timestamps
    end

    add_index :posts, :published
    add_index :posts, :created_at
  end
end
"""
        )

        # Create controllers
        create_file(
            project_path / "app/controllers/application_controller.rb",
            """class ApplicationController < ActionController::API
  before_action :authenticate_user!

  private

  def authenticate_user!
    token = request.headers['Authorization']&.split(' ')&.last
    return render json: { error: 'Not authorized' }, status: :unauthorized unless token

    @current_user = User.from_token(token)
    render json: { error: 'Invalid token' }, status: :unauthorized unless @current_user
  end

  def current_user
    @current_user
  end

  def authorize_admin!
    render json: { error: 'Forbidden' }, status: :forbidden unless current_user.admin?
  end
end
"""
        )

        create_file(
            project_path / "app/controllers/users_controller.rb",
            """class UsersController < ApplicationController
  skip_before_action :authenticate_user!, only: [:create]
  before_action :authorize_admin!, only: [:index, :destroy]
  before_action :set_user, only: [:show, :update, :destroy]

  def index
    @users = User.all
    render json: @users
  end

  def show
    render json: @user
  end

  def create
    @user = User.new(user_params)

    if @user.save
      render json: { user: @user, token: @user.generate_jwt_token }, status: :created
    else
      render json: { errors: @user.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def update
    if @user.update(user_params)
      render json: @user
    else
      render json: { errors: @user.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def destroy
    @user.destroy
    head :no_content
  end

  private

  def set_user
    @user = User.find(params[:id])
  end

  def user_params
    params.require(:user).permit(:username, :email, :password, :password_confirmation, :role)
  end
end
"""
        )

        create_file(
            project_path / "app/controllers/authentication_controller.rb",
            """class AuthenticationController < ApplicationController
  skip_before_action :authenticate_user!

  def login
    user = User.find_by(email: params[:email])

    if user&.authenticate(params[:password])
      render json: { user: user, token: user.generate_jwt_token }
    else
      render json: { error: 'Invalid credentials' }, status: :unauthorized
    end
  end
end
"""
        )

        # Create routes
        create_file(
            project_path / "config/routes.rb",
            """Rails.application.routes.draw do
  post '/auth/login', to: 'authentication#login'

  resources :users
  resources :posts
end
"""
        )

        # Create tests
        create_file(
            project_path / "spec/models/user_spec.rb",
            """require 'rails_helper'

RSpec.describe User, type: :model do
  describe 'validations' do
    it { should validate_presence_of(:email) }
    it { should validate_presence_of(:username) }
    it { should validate_uniqueness_of(:email) }
    it { should validate_uniqueness_of(:username) }
  end

  describe 'associations' do
    it { should have_many(:posts).dependent(:destroy) }
  end

  describe '#generate_jwt_token' do
    let(:user) { create(:user) }

    it 'generates a valid JWT token' do
      token = user.generate_jwt_token
      expect(token).to be_present
    end
  end
end
"""
        )

        create_file(
            project_path / "spec/requests/users_spec.rb",
            """require 'rails_helper'

RSpec.describe 'Users API', type: :request do
  describe 'POST /users' do
    let(:valid_params) do
      {
        user: {
          username: 'testuser',
          email: 'test@example.com',
          password: 'password123'
        }
      }
    end

    it 'creates a new user' do
      post '/users', params: valid_params
      expect(response).to have_http_status(:created)
      expect(JSON.parse(response.body)).to have_key('token')
    end
  end
end
"""
        )

        # Create README
        create_file(
            project_path / "README.md",
            """# Rails API

A sample Ruby on Rails API application.
"""
        )

        # Initialize git
        import subprocess
        subprocess.run(["git", "init"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "add", "."], cwd=str(project_path), check=True, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(project_path), check=True, capture_output=True)

        yield project_path


class TestRailsIntegration:
    """Integration tests for Ruby on Rails project analysis"""

    def test_analyze_basic_structure(self, rails_project):
        """Test that analyze() returns basic result structure"""
        analyzer = ProjectAnalyzer(str(rails_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        assert "analysis_id" in result
        assert "timestamp" in result
        assert "project_path" in result
        assert result["project_path"] == str(rails_project)

    def test_branch_creation_rails(self, rails_project):
        """Test that feature branch is created"""
        analyzer = ProjectAnalyzer(str(rails_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        branch_name = result["branch"]["branch"]
        assert branch_name.startswith("feature/import-")
        assert result["branch"]["created"] is True

    def test_directory_scan_rails(self, rails_project):
        """Test directory scanning"""
        analyzer = ProjectAnalyzer(str(rails_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        scan = result["scan"]
        assert scan["total_files"] >= 5
        assert ".rb" in scan["files_by_extension"]

        rb_info = scan["files_by_extension"][".rb"]
        assert rb_info["count"] >= 5
        assert rb_info["loc"] > 0

    def test_project_validation_rails(self, rails_project):
        """Test project validation"""
        analyzer = ProjectAnalyzer(str(rails_project))
        assert analyzer.validate_project() is True

    def test_language_detection_rails(self, rails_project):
        """Test language detection"""
        analyzer = ProjectAnalyzer(str(rails_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        lang_analysis = result["language_analysis"]
        assert lang_analysis["primary_language"] == "ruby"
        assert "ruby" in lang_analysis["languages"]
        assert lang_analysis["languages"]["ruby"]["percentage"] > 50

    def test_decision_extraction_rails(self, rails_project):
        """Test decision extraction"""
        analyzer = ProjectAnalyzer(str(rails_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        decisions = result["decisions"]
        assert "count" in decisions
        assert decisions["count"] >= 0

    def test_diagram_generation_rails(self, rails_project):
        """Test diagram generation"""
        analyzer = ProjectAnalyzer(str(rails_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        diagrams = result["diagrams"]
        assert isinstance(diagrams["diagrams"], list)

    def test_threat_modeling_rails(self, rails_project):
        """Test threat modeling"""
        analyzer = ProjectAnalyzer(str(rails_project))
        result = analyzer.analyze(skip_threat_model=False, skip_tech_debt=True)

        threats = result["threats"]
        if "status" in threats:
            assert threats["status"] != "skipped"

    def test_tech_debt_detection_rails(self, rails_project):
        """Test tech debt detection"""
        analyzer = ProjectAnalyzer(str(rails_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=False)

        tech_debt = result["tech_debt"]
        if "status" in tech_debt:
            assert tech_debt["status"] != "skipped"

    def test_documentation_generation_rails(self, rails_project):
        """Test documentation generation"""
        analyzer = ProjectAnalyzer(str(rails_project))
        result = analyzer.analyze(skip_threat_model=True, skip_tech_debt=True)

        docs = result["documentation"]
        assert isinstance(docs["adrs"], list)
        assert isinstance(docs["threat_model"], str)
        assert isinstance(docs["tech_debt_report"], str)
        assert isinstance(docs["import_report"], str)

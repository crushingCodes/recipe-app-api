import React from "react";
import {
    BrowserRouter as Router,
    Switch,
    Route,
    Link
} from "react-router-dom";
import { Layout, Menu, Breadcrumb, PageHeader } from 'antd';
import './App.css';
import 'antd/dist/antd.css';
import Recipes from './pages/Recipes';
const { Header, Content, Footer, Sider } = Layout;

export default class App extends React.Component {
    state = {
        collapsed: false,
    };

    onCollapse = collapsed => {
        console.log(collapsed);
        this.setState({ collapsed });
    };

    render() {
        const { collapsed } = this.state;

        return(
            <Router>
                <Layout style={{ minHeight: '100vh' }}>

                    <Sider collapsible collapsed={collapsed} onCollapse={this.onCollapse}>
                        <div className="logo" />
                        <Menu theme="dark" defaultSelectedKeys={['1']} mode="inline">

                            <Menu.Item key="1">
                                <Link to="/">Home</Link>
                            </Menu.Item>
                            <Menu.Item key="2">
                                <Link to="/recipes">Recipes</Link>
                            </Menu.Item>
                            <Menu.Item key="3">
                                <Link to="/about">About</Link>
                            </Menu.Item>
                        </Menu>
                    </Sider>
                    <Layout className="site-layout">
                        <Header className="site-layout-background" style={{ padding: 0 }} >
                            <PageHeader
                                className="site-page-header"
                                title="Video Recipes"
                                subTitle="This is a subtitle"
                            />
                        </Header>
                        <Content style={{ margin: '0 16px' }}>
                            <Breadcrumb style={{ margin: '16px 0' }}>
                                <Breadcrumb.Item>Recipes</Breadcrumb.Item>
                                <Breadcrumb.Item>Breakfast</Breadcrumb.Item>
                            </Breadcrumb>
                            <div className="site-layout-background" style={{ padding: 24, minHeight: 360 }}>
                                <Switch>
                                    <Route path="/about">
                                        <About />
                                    </Route>
                                    <Route path="/recipes">
                                        <Recipes />
                                    </Route>
                                    <Route path="/">
                                        <Home />
                                    </Route>
                                </Switch>

                            </div>
                        </Content>
                        <Footer style={{ textAlign: 'center' }}>Ant Design ©2018 Created by Ant UED</Footer>
                    </Layout>
                </Layout>
            </Router>
        )
    }
}

function Home() {
    return <h2>Home</h2>;
}

function About() {
    return <h2>About</h2>;
}
